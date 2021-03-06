from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from .models import User, Task, Collection

"""
    TEMPLATES
"""

def index(request):
    return render(request, 'index.html')

def homepage(request):
    if "user_id" not in request.session:
        messages.error(request, "Must be logged in")
        return redirect('/')
    user_id = request.session['user_id']
    collection = Collection.objects.get(title = "General", user_id = request.session['user_id'])
    print(collection)
    collections = Collection.objects.all().filter(user_id = request.session['user_id']).exclude(title = "General")
    context = {
        "user": User.objects.get(id=user_id),
        "general_tasks": Task.objects.filter(user_id = user_id, collection_id = collection.id).order_by('-created_at'),
        "user_collections": collections.order_by('updated_at'),
    }
    return render(request, 'homepage.html', context)

def collectionsPage (request):
    if "user_id" not in request.session:
        messages.error(request, "Must be logged in")
        return redirect('/')
    
    user_id = request.session['user_id']

    context = {
        "user": User.objects.get(id=user_id),
        "user_collections": Collection.objects.filter(user_id = request.session['user_id']).order_by('updated_at')
    }
    return render(request, "collectionsPage.html", context)

def singleCollection(request, title):
    if 'user_id' not in request.session:
       messages.error(request, 'Must be logged in')
       return redirect('/')
    collection = Collection.objects.get(title = title, user_id = request.session['user_id'])
    context = {
        "collection": collection,
        "tasks": collection.tasks.all().order_by("-created_at"),
        "user": User.objects.get(id = request.session['user_id']),
    }
    return render(request, "singleCollection.html", context)

"""
    LOGIN/REGISTER PROCESS
"""

def register(request):
    post = request.POST
    errors = User.objects.basic_validator(post)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    lowerCaseEmail = post['email'].lower()
    if User.objects.filter(email = lowerCaseEmail).exists():
        messages.error(request, "That email already exists")
        return redirect('/')
    capitalizedFirstName = post['first_name'].capitalize()
    capitalizedLastName = post['last_name'].capitalize()
    password = post['password']
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User.objects.create(
        first_name = capitalizedFirstName, 
        last_name = capitalizedLastName, 
        email = lowerCaseEmail, 
        password = pw_hash
    )
    Collection.objects.create(
        title = "General",
        desc = "Things that just need to get done.",
        user = user
    )
    request.session['user_id'] = user.id
    return redirect('/homepage')

def login(request):
    post = request.POST
    lowerEmail = post['email'].lower()
    try:
        user = User.objects.get(email = lowerEmail)
    except:
        messages.error(request, "Please check your password or email.")
        return redirect('/')

    if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        request.session["user_id"] = user.id
        return redirect('/homepage')
    else:
        messages.error(request, "please check your email and password.")
        return redirect('/')

def logout(request):
    request.session.clear()
    return redirect('/')

"""
    PROCESS FOR TASKS / COLLECTIONS
"""

# DELETE ***********
def deleteHomepageTask(request, taskId):
    if "user_id" not in request.session:
        messages.error(request, "Must be logged in")
        return redirect('/')
    task = Task.objects.get(id = taskId)
    user = User.objects.get(id = request.session["user_id"])
    print(task and user)
    if task.user_id != user.id:
        user.delete()
        return redirect('/')
    else:
        task.delete()
        return redirect('/homepage')

def deleteCollFromHome(request, colId):
    if 'user_id' not in request.session:
       messages.error(request, 'Must be logged in')
       return redirect('/')
    collection = Collection.objects.get(id = colId)
    user = User.objects.get(id = request.session['user_id'])
    post = request.POST
    if collection.user_id != user.id:
        user.delete()
        return redirect('/')
    else:
        collection.delete()
        return redirect('/homepage')

def deleteCollFromColl(request, colId):
    if 'user_id' not in request.session:
       messages.error(request, 'Must be logged in')
       return redirect('/')
    collection = Collection.objects.get(id = colId)
    user = User.objects.get(id = request.session['user_id'])
    post = request.POST
    if collection.user_id != user.id:
        user.delete()
        return redirect('/')
    else:
        collection.delete()
        return redirect('/collections')

def deleteTaskFromSingleColl(request, collId,taskId):
    if 'user_id' not in request.session:
       messages.error(request, 'Must be logged in')
       return redirect('/')
    collection = Collection.objects.get(id = collId)
    Task.objects.get(id = taskId).delete()
    return redirect(f'/collections/{collection.title}')

# CREATE **********
def createGenTask(request):
    if "user_id" not in request.session:
        messages.error(request, "Must be logged in")
        return redirect('/')
    post = request.POST
    errors = Task.objects.basic_validator(post)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/homepage')
    Task.objects.create(
        content = post['content'].capitalize(),
        user = User.objects.get(id = request.session['user_id']),
        collection = Collection.objects.get(title = "General", user_id = request.session['user_id'])
    )
    return redirect('/homepage')

def createCollection(request):
    if "user_id" not in request.session:
        messages.error(request, "Must be logged in")
        return redirect('/')
    post = request.POST
    Collection.objects.create(
        title = post['title'].capitalize(),
        user = User.objects.get(id = request.session['user_id']),
    )
    return redirect('/collections')

def createTaskForSingleCollection(request):
    post = request.POST
    collection = Collection.objects.get(id = post["id"], user_id = request.session['user_id'])
    user = User.objects.get(id=request.session['user_id'])
    Task.objects.create(
        content= post["content"],
        user= user,
        collection= collection,
    )
    return redirect(f'/collections/{collection.title}')









