from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from forms import PublicationForm, AuthorForm, BookForm, ConferenceForm, JournalForm, MagazineForm, PosterForm
from forms import PresentationForm, TechnicalReportForm, OtherForm
from forms import ExperimentForm, FrequencyForm, KeywordForm, ModelForm, VariableForm
import requests
from django.http import JsonResponse
import pdb


@login_required()
def index(request):
    return render(request, 'site/search.html')


@login_required()
def review(request):
    return render(request, 'site/review.html')


@login_required()
def search(request):
    return render(request, 'site/search.html')


@login_required()
def new(request):
    if request.method == 'GET':
        return render(request, 'site/new_publication.html')
    elif request.method == 'POST':
        pub_form = PublicationForm(request.POST, prefix='pub')
        pub_type =  request.POST.get('pub_type', '')
        if pub_type == 'Book':
            media_form = BookForm(request.POST, prefix='book')
            if media_form.is_valid() and pub_form.is_valid():
                pub_form.save(commit=False)
                media_form.save(commit=False)
                return HttpResponse(status=200)
        elif pub_type == 'Conference':
            media_form = ConferenceForm(request.POST, prefix='conf')
        elif pub_type == 'Journal':
            media_form = JournalForm(request.POST, prefix='journal')
        elif pub_type == 'Magazine':
            media_form = MagazineForm(request.POST, prefix='mag')
        elif pub_type == 'Poster':
            media_form = PosterForm(request.POST, prefix='poster')
        elif pub_type == 'Presentation':
            media_form = PresentationForm(request.POST, prefix='pres')
        elif pub_type == 'Technical_Report':
            media_form = TechnicalReportForm(request.POST, prefix='tech')
        elif pub_type == 'Other':
            media_form = OtherForm(request.POST, prefix='other')

        JsonResponse({'pub_form': pub_form, 'media_form': media_form}, status=400) # These should be strings actually

def finddoi(request):
    doi = request.GET.get('doi')
    if not doi or doi.isspace():
        empty = True
    else:
        empty = False
        accept = 'application/vnd.citationstyles.csl+json; locale=en-US'
        headers = {'accept': accept}
        if doi[:5].lower() == 'doi: ':  # grabs first 5 characters lowercases, and compares
            try:
                url = "http://dx.doi.org/" + doi.split()[1]  # removes "doi:" and whitespace leaving only the doi
            except IndexError:
                return (doi.strip('\n') + " -- Invalid DOI.\n")
        elif doi.startswith('doi:10'):
            url = "http://dx.doi.org/" + doi[4:]  # remove 'doi:'
        elif doi.startswith("http://dx.doi.org/"):
            url = doi
        else:
            url = "http://dx.doi.org/" + doi
        r = requests.get(url, headers=headers)
    if not empty and r.status_code == 200:

        # TODO: Catch differences between agencies e.g. Crossref vs DataCite
        initial = r.json()
        if 'DOI' in initial.keys():
            doi = initial['DOI']
        else:
            doi = ''
        if 'ISBN' in initial.keys():
            isbn = initial['ISBN']
        else:
            isbn = ''
        if 'title' in initial.keys():
            title = initial['title']
        else:
            title = ''
        if 'URL' in initial.keys():
            url = requests.get(initial['URL'], stream=True, verify=False).url  # use llnl cert instead of verify=False
        else:
            url = ''
        if 'page' in initial.keys():
            page = initial['page']
        else:
            page = ''
        if 'publisher' in initial.keys():
            publisher = initial['publisher']
        else:
            publisher = ''
        if 'published-print' in initial.keys():
            publication_date = initial['published-print']['date-parts'][0][0]
        else:
            publication_date = ''
        if 'author' in initial.keys():
            authors_list = []
            AuthorFormSet = formset_factory(AuthorForm, extra=0)
            if 'given' in initial['author'][0].keys():
                for author in initial['author']:
                    authors_list.append({'first_name': author['given'], 'last_name': author['family']})
                author_form = AuthorFormSet(initial=authors_list)
            elif 'literal' in initial['author'][0].keys():
                for author in initial['author']:
                    authors_list.append({'first_name': author['literal']})
                author_form = AuthorFormSet(initial=authors_list)
            else:
                AuthorFormSet = formset_factory(AuthorForm, extra=1)
                author_form = AuthorFormSet()
        else:
            AuthorFormSet = formset_factory(AuthorForm, extra=1)
            author_form = AuthorFormSet()

        init = {'doi': doi, 'isbn': isbn, 'title': title, 'url': url, 'page': page, 'publisher': publisher,
                'publication_date': publication_date}
        pub_form = PublicationForm(prefix='pub', initial=init)
        book_form = BookForm(prefix='book', initial={'publisher': publisher, 'publication_date': publication_date})
        conference_form = ConferenceForm(prefix='conf')
        journal_form = JournalForm(prefix='journal')
        magazine_form = MagazineForm(prefix='mag')
        poster_form = PosterForm(prefix='poster')
        presentation_form = PresentationForm(prefix='pres')
        technical_form = TechnicalReportForm(prefix='tech')
        other_form = OtherForm(prefix='other')
        exp_form = ExperimentForm()
        freq_form = FrequencyForm()
        keyword_form = KeywordForm()
        model_form = ModelForm()
        var_form = VariableForm()
        return render(request, 'site/publication_details.html',
                      {'pub_form': pub_form, 'author_form': author_form,
                       'book_form': book_form,
                       'conference_form': conference_form,
                       'journal_form': journal_form, 'magazine_form': magazine_form, 'poster_form': poster_form,
                       'presentation_form': presentation_form, 'technical_form': technical_form,
                       'other_form': other_form, 'exp_form': exp_form, 'freq_form': freq_form,
                       'keyword_form': keyword_form, 'model_form': model_form, 'var_form': var_form})
    else:
        pub_form = PublicationForm(prefix='pub')
        AuthorFormSet = formset_factory(AuthorForm, extra=1)
        author_form = AuthorFormSet()
        book_form = BookForm(prefix='book')
        conference_form = ConferenceForm(prefix='conf')
        journal_form = JournalForm(prefix='journal')
        magazine_form = MagazineForm(prefix='mag')
        poster_form = PosterForm(prefix='poster')
        presentation_form = PresentationForm(prefix='pres')
        technical_form = TechnicalReportForm(prefix='tech')
        other_form = OtherForm(prefix='other')
        exp_form = ExperimentForm()
        freq_form = FrequencyForm()
        keyword_form = KeywordForm()
        model_form = ModelForm()
        var_form = VariableForm()
        return render(request, 'site/publication_details.html',
                      {'pub_form': pub_form, 'author_form': author_form, 'book_form': book_form,
                       'conference_form': conference_form,
                       'journal_form': journal_form, 'magazine_form': magazine_form, 'poster_form': poster_form,
                       'presentation_form': presentation_form, 'technical_form': technical_form,
                       'other_form': other_form, 'exp_form': exp_form, 'freq_form': freq_form,
                       'keyword_form': keyword_form, 'model_form': model_form, 'var_form': var_form,
                       'message': 'Unable to pre-fill form with the given DOI'})
