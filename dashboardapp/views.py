# views.py
# --- Standard imports ---
import os, csv, json
from io import BytesIO
from decimal import Decimal
from collections import defaultdict
from typing import List

# --- Django core ---
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DeleteView, DetailView, ListView

# --- QR code ---
import qrcode

# --- App-specific models and forms ---
from .models import Dashboard, UserCSV, UserProfile, CSVHeading, CSVValue
from .forms import DashboardForm, CSVUploadForm

# --- OpenAI integration (via LangChain) ---
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate

def index(request):
    """Render the home page."""
    return render(request, "home.html")

@login_required
def dashboard_list(request):
    """Render a list of dashboards owned by the currently logged-in user."""
    dashboards = Dashboard.objects.filter(user__user=request.user)
    return render(request, "dashboard_list.html", {"dashboards": dashboards})

@login_required
def dashboard_create(request):
    """
    Handle dashboard creation. If POST, saves a new dashboard and generates
    a QR code pointing to the dashboard's detail URL.
    """
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            dashboard = form.save(commit=False)
            dashboard.user = request.user.userprofile
            dashboard.save()

            # Build share URL
            share_url = request.build_absolute_uri(
                reverse('dashboard_detail', kwargs={
                    'user_pk': dashboard.user.pk,
                    'dashboard_pk': dashboard.pk
                })
            )

            # Generate QR code
            img = qrcode.make(share_url)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Use predictable filename
            filename = f"dashboard_{dashboard.user.pk}_{dashboard.pk}_qr.png"
            dashboard.qr_code_image.save(filename, ContentFile(buffer.read()), save=True)

            return redirect('dashboard_list')
    else:
        form = DashboardForm()

    return render(request, 'dashboard_form.html', {'form': form})


@csrf_exempt
@login_required
def save_dashboard_layout(request, user_pk, dashboard_pk):
    """
    Save the layout JSON of a dashboard. Called via JavaScript using fetch().
    Only accessible by the dashboard owner.
    """
    if request.method == 'POST':
        dashboard = get_object_or_404(Dashboard, pk=dashboard_pk, user__pk=user_pk, user__user=request.user)
        data = json.loads(request.body)
        dashboard.layout_json = data.get("layout")
        dashboard.save()
        return JsonResponse({'status': 'ok'})


@login_required
def csv_list(request):
    """Render a list of CSVs uploaded by the currently logged-in user."""
    csvs = UserCSV.objects.filter(user__user=request.user)
    return render(request, "csv_list.html", {"csvs": csvs})

@login_required
def csv_upload(request):
    """
    Handle CSV file upload. If POST and valid, store file and parse its contents
    into CSVHeading and CSVValue model instances.
    """
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_obj = form.save(commit=False)
            csv_obj.user = request.user.userprofile
            csv_obj.save()

            # Parse the uploaded CSV
            file = csv_obj.csv_file.open('r')
            reader = csv.reader(file)
            headers = next(reader, None)

            if headers:
                heading_objs = [CSVHeading.objects.create(csv=csv_obj, heading_name=h) for h in headers]
                for row_idx, row in enumerate(reader):
                    for heading_obj, val in zip(heading_objs, row):
                        CSVValue.objects.create(csv=csv_obj, heading=heading_obj, row_index=row_idx, value=val)

            return redirect('csv_list')
        return render(request, 'csv_form.html', {'form': form})
    else:
        form = CSVUploadForm()
    return render(request, 'csv_form.html', {'form': form})

def dashboard_detail(request, user_pk, dashboard_pk):
    """
    Render a dashboard's editable or read-only view.
    If POST and user is owner, update the dashboard's title.
    Also detects column types for chart creation support.
    """
    dashboard = get_object_or_404(Dashboard, pk=dashboard_pk, user__pk=user_pk)
    is_owner = dashboard.user.user == request.user

    if is_owner and request.method == "POST":
        form = DashboardForm(request.POST, instance=dashboard)
        if form.is_valid():
            dashboard = form.save(commit=False)
            dashboard.is_public = False
            dashboard.save()
            messages.success(request, "Dashboard title updated successfully.")
    else:
        form = DashboardForm(instance=dashboard) if is_owner else None

    # Find CSV information for logged in users
    if request.user.is_authenticated:
        user_csvs = UserCSV.objects.filter(user__user=request.user)
        headings = CSVHeading.objects.filter(csv__in=user_csvs).distinct()
    else:
        user_csvs = UserCSV.objects.none()
        headings = CSVHeading.objects.none()

    column_types = {}
    for heading in headings:
        values = CSVValue.objects.filter(heading=heading).values_list('value', flat=True)[:10]
        is_numeric = True
        for val in values:
            try:
                Decimal(val)
            except:
                is_numeric = False
                break
        column_types[heading.heading_name] = 'numeric' if is_numeric else 'text'

    columns = list(column_types.keys())  # ✅ Add this line

    return render(request, "dashboard_detail.html", {
        "dashboard": dashboard,
        "form": form,
        "is_owner": is_owner,
        "column_types": column_types,
        "columns": columns,
    })

# --- Get data for chart creation ---
@require_POST
@login_required
@csrf_exempt  # if you're calling via fetch(), or set CSRF token properly
def get_chart_data(request):
    """
    API endpoint that receives column selections and returns chart-ready
    labels and data values. Handles numeric aggregation (sum/avg) or
    categorical counting (for pie charts).
    """
    try:
        data = json.loads(request.body)
        x_col = data['xCol']
        y_col = data.get('yCol')
        agg = data.get('agg', 'none')

        # Get user's CSVs and find the one that contains both headings
        user_csvs = UserCSV.objects.filter(user__user=request.user)
        x_heading = CSVHeading.objects.filter(csv__in=user_csvs, heading_name=x_col).first()
        y_heading = CSVHeading.objects.filter(csv__in=user_csvs, heading_name=y_col).first() if y_col else None

        if not x_heading or (y_col and not y_heading):
            return JsonResponse({"error": "Invalid column selection"}, status=400)

        # Fetch values
        x_values_qs = CSVValue.objects.filter(heading=x_heading)
        data_map = defaultdict(list)

        for val in x_values_qs:
            x_val = val.value
            if y_heading:
                y_val = CSVValue.objects.filter(
                    heading=y_heading,
                    csv=x_heading.csv,
                    row_index=val.row_index
                ).first()
                if y_val:
                    try:
                        y_val_num = Decimal(y_val.value)
                        data_map[x_val].append(y_val_num)
                    except:
                        pass  # skip non-numeric
            else:
                data_map[x_val].append(1)  # count occurrences for pie chart

        # Aggregate
        labels, values = [], []
        for key, nums in data_map.items():
            labels.append(key)
            if agg == "sum":
                values.append(float(sum(nums)))
            elif agg == "avg":
                values.append(float(sum(nums) / len(nums)) if nums else 0)
            else:  # 'none' or pie count
                values.append(float(nums[0] if y_heading else sum(nums)))

        return JsonResponse({
            "labels": labels,
            "data": values,
            "xLabel": x_col,
            "yLabel": y_col or ""
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# --- Dashboard Update/Delete ---

@method_decorator(login_required, name='dispatch')
class DashboardUpdateView(UpdateView):
    """Class-based view for updating a dashboard title."""
    model = Dashboard
    fields = ['title']
    template_name = 'dashboard_form.html'
    success_url = reverse_lazy('dashboard_list')

    def get_queryset(self):
        return Dashboard.objects.filter(user__user=self.request.user)


@method_decorator(login_required, name='dispatch')
class DashboardDeleteView(DeleteView):
    """Class-based view for deleting a dashboard."""
    model = Dashboard
    template_name = 'dashboard_confirm_delete.html'
    success_url = reverse_lazy('dashboard_list')

    def get_queryset(self):
        return Dashboard.objects.filter(user__user=self.request.user)


# --- UserCSV Update/Delete ---

@method_decorator(login_required, name='dispatch')
class UserCSVUpdateView(UpdateView):
    """Class-based view for updating a user's uploaded CSV file."""
    model = UserCSV
    form_class = CSVUploadForm  # Use your form instead of 'fields'
    template_name = 'csv_form.html'
    success_url = reverse_lazy('csv_list')

    def get_queryset(self):
        return UserCSV.objects.filter(user__user=self.request.user)

@method_decorator(login_required, name='dispatch')
class UserCSVDeleteView(DeleteView):
    """Class-based view for deleting a user's uploaded CSV file."""
    model = UserCSV
    template_name = 'csv_confirm_delete.html'
    success_url = reverse_lazy('csv_list')

    def get_queryset(self):
        return UserCSV.objects.filter(user__user=self.request.user)


# --- QR Code Generation ---

@login_required
def generate_qr_code(request, dashboard_id):
    """
    Return the QR code URL and shareable link for the given dashboard.
    Only accessible to the owner.
    """
    dashboard = get_object_or_404(Dashboard, id=dashboard_id, user__user=request.user)

    share_url = request.build_absolute_uri(
        reverse('dashboard_detail', kwargs={
            'user_pk': dashboard.user.pk,
            'dashboard_pk': dashboard.pk
        })
    )

    return JsonResponse({
        "qr_url": dashboard.qr_code_image.url,
        "share_url": share_url
    })

# --- OpenAI API integration ---

@login_required
def chatui(request):
    """Render the Chat UI page that uses OpenAI via LangChain."""
    return render(request, "chatui.html")

@csrf_exempt
@login_required
def chatbot(request):
    """
    Handle POST requests to the chatbot endpoint.
    Accepts conversation history and returns a response from the OpenAI model.
    """
    if request.method == "POST":
        try:
            history = json.loads(request.body)
            prompt = ChatPromptTemplate.from_messages(history)
            llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.7)
            chain = prompt | llm
            response = chain.invoke({})
            return JsonResponse({"message": response.content})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)