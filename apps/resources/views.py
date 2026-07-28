from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Area, Resource


def resource_list(request):
    resources = Resource.objects.select_related("area").filter(is_active=True)
    area = request.GET.get("area")
    resource_type = request.GET.get("type")
    query = request.GET.get("q")
    if area:
        resources = resources.filter(area_id=area)
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if query:
        resources = resources.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(
        request,
        "resources/resource_list.html",
        {
            "resources": resources,
            "areas": Area.objects.all(),
            "types": Resource.Type.choices,
            "now": timezone.now(),
        },
    )


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource.objects.select_related("area"), pk=pk, is_active=True)
    return render(request, "resources/resource_detail.html", {"resource": resource})
