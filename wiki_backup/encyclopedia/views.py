from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import random
import markdown2

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': 'form-control'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    else:
        html_content = markdown2.markdown(content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })

def search(request):
    query = request.GET.get('q', '')
    if util.get_entry(query):
        return HttpResponseRedirect(reverse("entry", kwargs={"title": query}))
    else:
        entries = util.list_entries()
        results = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "results": results,
            "query": query
        })

def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):
                return render(request, "encyclopedia/new_page.html", {
                    "form": form,
                    "error": "An entry with this title already exists."
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
    else:
        return render(request, "encyclopedia/new_page.html", {
            "form": NewPageForm()
        })

def edit_page(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["content"]
            util.save_entry(title, new_content)
            return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
    else:
        form = NewPageForm(initial={"title": title, "content": content})
        return render(request, "encyclopedia/edit_page.html", {
            "form": form,
            "title": title
        })

def random_page(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return HttpResponseRedirect(reverse("entry", kwargs={"title": random_entry}))
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries available."
        })