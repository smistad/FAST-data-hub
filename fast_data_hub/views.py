from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from fast_data_hub.models import Item


def index(request):
    return render(request, 'fast_data_hub/index.html')


def pipelines(request):
    return render(request, 'fast_data_hub/pipelines.html', {
        'items': Item.objects.filter(is_pipeline=True)
    })


def models(request):
    return render(request, 'fast_data_hub/models.html', {
        'items': Item.objects.filter(is_model=True)
    })


def data(request):
    return render(request, 'fast_data_hub/data.html', {
        'items': Item.objects.filter(is_data=True)
    })


def api_get_item_files(request, item_id):
    """
    Retrieve an item, and return json list of files needed to download
    """
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        raise Http404('Item does not exist')

    return JsonResponse(item.toJSON(request))


def api_get_list(request, tag):
    try:
        item_objects = Item.objects.filter(tag__name=tag)
    except:
        raise Http404()

    items = []
    for item in item_objects:
        items.append(item.toJSON(request))

    return JsonResponse({'items': items})


def api_get_pipeline_text(request, item_id):
    try:
        pipeline = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        raise Http404()

    return JsonResponse({'text': pipeline.pipeline_text})


def download(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        item.download_counter += 1
        item.save()

        if len(item.external_url) > 0:
            redirect_url = item.external_url
        elif len(item.pipeline_text) > 0:
            redirect_url = request.build_absolute_uri(reverse('api_get_pipeline', kwargs={'item_id': item_id}))
        else:
            redirect_url = request.build_absolute_uri(f'/uploads/{item.id}/data.zip')

        return HttpResponseRedirect(redirect_url)
    except Item.DoesNotExist:
        raise Http404()