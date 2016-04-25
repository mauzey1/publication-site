from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms import forms, formset_factory, modelformset_factory
from forms import PublicationForm, AuthorForm, BookForm, ConferenceForm, JournalForm, MagazineForm, PosterForm
from forms import PresentationForm, TechnicalReportForm, OtherForm
from forms import ExperimentForm, FrequencyForm, KeywordForm, ModelForm, VariableForm
import requests
from django.http import JsonResponse
from models import *
import pdb


@login_required()
def index(request):
    return render(request, 'site/search.html')


@login_required()
def search(request):
    return render(request, 'site/search.html')


@login_required()
def review(request):
    message = None
    userid = request.user.id
    entries = Publication.objects.filter(submitter=userid)
    if not entries:
        message = 'You do not have any publications to display. <a href="/new">Submit one.</a>'
    return render(request, 'site/review.html', {'message': message, 'entries': entries, 'error': None})


@login_required()
def edit(request, pubid):
    if request.method == 'POST':
        pub_instance = Publication.objects.get(id=pubid)
        pub_form = PublicationForm(request.POST or None, instance=pub_instance)
        AuthorFormSet = formset_factory(AuthorForm)
        author_form_set = AuthorFormSet(request.POST)

        pub_type = request.POST.get('pub_type', '')
        # todo: helper functions
        if pub_type == 0:  # book
            media_form = BookForm(request.POST)
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency = ([Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords = ([Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model = ([Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables = ([Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                journal = media_form.save(commit=False)
                journal.publication_id = publication
                journal.save()
                return HttpResponse(status=200)
        elif pub_type == 1:  # conference
            media_form = ConferenceForm(request.POST)
        elif pub_type == 2:  # journal
            media_form = JournalForm(request.POST)
        elif pub_type == 3:  # magazine
            media_form = MagazineForm(request.POST)
        elif pub_type == 4:  # poster
            media_form = PosterForm(request.POST)
        elif pub_type == 5:  # presentation
            media_form = PresentationForm(request.POST)
        elif pub_type == 6:  # technical report
            media_form = TechnicalReportForm(request.POST)
        elif pub_type == 7:  # other
            media_form = OtherForm(request.POST)

    else:
        publication = Publication.objects.get(id=pubid)
        authors = publication.authors.all()
        userid = request.user.id
        if userid == publication.submitter.id:
            pub_form = PublicationForm(instance=publication)
            AuthorFormSet = modelformset_factory(Author, AuthorForm, extra=0)
            author_form = AuthorFormSet(queryset=authors)
            if publication.publication_type == 0: # book
                media_form = BookForm(instance=Book.objects.get(publication_id=publication))
            elif publication.publication_type == 1: # conference
                media_form = ConferenceForm(instance=Conference.objects.get(publication_id=publication))
            elif publication.publication_type == 2:  # journal
                media_form = JournalForm(instance=Journal.objects.get(publication_id=publication))
            elif publication.publication_type == 3:  # magazine
                media_form = MagazineForm(instance=Magazine.objects.get(publication_id=publication))
            elif publication.publication_type == 4:  # poster
                media_form = PosterForm(instance=Poster.objects.get(publication_id=publication))
            elif publication.publication_type == 5:  # presentation
                media_form = PresentationForm(instance=Presentation.objects.get(publication_id=publication))
            elif publication.publication_type == 6:  # technical report
                media_form = TechnicalReportForm(instance=TechnicalReport.objects.get(publication_id=publication))
            elif publication.publication_type == 7:  # other
                media_form = OtherForm(instance=Other.objects.get(publication_id=publication))
            freq_form = FrequencyForm(initial={'frequency': [box.id for box in publication.frequency.all()]})
            exp_form = ExperimentForm(initial={'exp': [box.id for box in publication.experiments.all()]})
            keyword_form = KeywordForm(initial={'keyword': [box.id for box in publication.keywords.all()]})
            model_form = ModelForm(initial={'model': [box.id for box in publication.model.all()]})
            var_form = VariableForm(initial={'variable': [box.id for box in publication.variables.all()]})
            return render(request, 'site/edit.html',
                          {'pub_form': pub_form, 'author_form': author_form, 'freq_form': freq_form, 'exp_form': exp_form, 'keyword_form': keyword_form,
                           'model_form': model_form, 'var_form': var_form, 'media_form': media_form, 'pub_type': publication.publication_type,
                           })
        else:
            entries = Publication.objects.filter(submitter=userid)
            error = 'Error: You must be the owner of a submission to edit it.'
            return render(request, 'site/review.html', {'message': None, 'entries': entries, 'error': error})


@login_required()
def new(request):
    if request.method == 'GET':
        return render(request, 'site/new_publication.html')
    elif request.method == 'POST':
        pub_form = PublicationForm(request.POST, prefix='pub')
        AuthorFormSet = formset_factory(AuthorForm)
        author_form_set = AuthorFormSet(request.POST)
        pub_type = request.POST.get('pub_type', '')
        if pub_type == 'Book':
            media_form = BookForm(request.POST, prefix='book')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                # todo: make this a function
                # --------------------------
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 0
                publication.save()
                ensemble = request.POST.getlist('ensemble')
                for exp_id in request.POST.getlist("experiment"):
                    exp = Experiment.objects.get(id=exp_id)
                    ens = ensemble[exp.id-1] #database index vs lists, so off by one
                    if ens:
                        PubModels.objects.create(publication=publication, experiment=exp, ensemble=ens)
                        print PubModels.objects.all()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                # -------------------------
                book = media_form.save(commit=False)
                book.publication_id = publication
                book.save()
                return HttpResponse(status=200)

        elif pub_type == 'Conference':
            media_form = ConferenceForm(request.POST, prefix='conf')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 1
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                conference = media_form.save(commit=False)
                conference.publication_id = publication
                conference.save()
                return HttpResponse(status=200)
        elif pub_type == 'Journal':
            media_form = JournalForm(request.POST, prefix='journal')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 2
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                journal = media_form.save(commit=False)
                journal.publication_id = publication
                journal.save()
                return HttpResponse(status=200)
        elif pub_type == 'Magazine':
            media_form = MagazineForm(request.POST, prefix='mag')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 3
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                magazine = media_form.save(commit=False)
                magazine.publication_id = publication
                magazine.save()
                return HttpResponse(status=200)
        elif pub_type == 'Poster':
            media_form = PosterForm(request.POST, prefix='poster')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 4
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                poster = media_form.save(commit=False)
                poster.publication_id = publication
                poster.save()
                return HttpResponse(status=200)
        elif pub_type == 'Presentation':
            media_form = PresentationForm(request.POST, prefix='pres')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 5
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                presentation = media_form.save(commit=False)
                presentation.publication_id = publication
                presentation.save()
                return HttpResponse(status=200)
        elif pub_type == 'Technical_Report':
            media_form = TechnicalReportForm(request.POST, prefix='tech')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 6
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                techreport = media_form.save(commit=False)
                techreport.publication_id = publication
                techreport.save()
                return HttpResponse(status=200)
        elif pub_type == 'Other':
            media_form = OtherForm(request.POST, prefix='other')
            if media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
                publication = pub_form.save(commit=False)
                publication.submitter = request.user
                publication.save()
                publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
                publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
                publication.model.add(*[Model.objects.get(id=model_id) for model_id in request.POST.getlist("model")])
                publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
                publication.publication_type = 7
                publication.save()
                for authorform in author_form_set:
                    author = authorform.save()
                    publication.authors.add(author.id)
                other = media_form.save(commit=False)
                other.publication_id = publication
                other.save()
                return HttpResponse(status=200)

        return JsonResponse({'pub_form': pub_form.as_table(), 'media_form': media_form.as_table(), 'auth_form': author_form_set.as_table()},
                            status=400)  # These should be strings actually


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
