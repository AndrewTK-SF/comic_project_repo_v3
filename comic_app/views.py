from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, UserManager, Comic, Collection
from django.contrib import messages
from collections import Counter
import requests, time, hashlib, json, threading
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def login_val(request):
    if request.method!="POST":
        return redirect('/')
    else:
        errors = User.objects.login_validator(request.POST)
        if len(errors) != 0:
            for k, v in errors.items():
                messages.error(request, v)
            return redirect('/')
        user_email=User.objects.filter(email=request.POST['email_login'])
        request.session['user_id'] = user_email[0].id
        request.session['first_name']=user_email[0].first_name
        print(request.session['user_id'])
        return redirect('/landing')

def reg_val(request):
            #check for post errors(did not arrive via "GET")
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for k, v in errors.items():
                messages.error(request, v)
            return redirect('/register')
        #hash PW
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()   
        print(pw_hash)   
        #create user
        new_user=User.objects.create(
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name'],
        email=request.POST['email'],
        hashpass=pw_hash,
        )  
        print(new_user.first_name)
        #create session 
        request.session['user_id']=new_user.id
        request.session['first_name']=request.POST['first_name']
        return redirect('/success')
    return redirect('/register')

def success(request):
    new_user=User.objects.get(id=request.session['user_id'])
    context={
        'user':new_user
    }
    return render(request, 'success.html', context)

def add_comic(request):
    if request.method=='POST':
        errors = Comic.objects.comic_validator(request.POST)
    if len(errors) != 0:
        for k, v in errors.items():
            messages.error(request, v)
        return redirect('/landing')
    else:
        t = time.time()
        tr = round(t)
        ts = str(tr)
        pubk= os.getenv('API_pub')
        prik=os.getenv('API_pri')
        key = ts+prik+pubk
        hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        print(hash)
        book_upc=request.POST['upc']
        print(book_upc)
        com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={book_upc}&ts={ts}&apikey={pubk}&hash={hash}')
        com_json=com.json()
        com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
        print(com_dumps)
        print(len(com_dumps))
        user=User.objects.get(id=request.session['user_id'])
        library_test=user.uploader.filter(upc=book_upc)
        if len(library_test)>0:
            messages.info(request, 'This comic is already in your library')
            return HttpResponseRedirect('/landing')
        try: 
            book_title=com_json['data']['results'][0]['title']
        except:
            messages.info(request, 'I am sooooo sorry but that UPC will not work becuase the Marvel API is still in beta and will not return a JSON object that includes all the needed info for every UPC code!')
            return HttpResponseRedirect('/landing')
            # return HttpResponse('Invalid header found.')
        else:
            print(len(book_title))
            print(book_title)
            rel_date_type = com_json['data']['results'][0]['dates'][0]['type']
            rel_date = com_json['data']['results'][0]['dates'][0]['date']
            new_comic=Comic.objects.create(
                upc=book_upc,
                title=book_title,
                release_date=rel_date,
            )
            # uploaded_by=User.objects.get(id=request.session['user_id'])
            user.uploader.add(new_comic)
            # print(com_json['data']['results'][0]['dates'][0]['date'])
            # list = com_json['data']['results'][0]['creators']['items']
            # context={
            #     'type':q, 
            #     'date':x
            # }
            return redirect('/landing')

def landing(request):
    user=User.objects.get(id=request.session['user_id'])
    lists=Comic.objects.values('title','upc', 'favorite')
    arr=[]
    for list in lists:
        if list['favorite']!=None:
            arr.append(list['upc'])
        else:
            print('crap')
    print(arr)
    count=Counter(arr)
    print(count)
    new=count.most_common()
    print(new)
    (j,_)=(new[0])
    winner=j
    print(winner)
    t = time.time()
    tr = round(t)
    ts = str(tr)
    pubk= os.getenv('API_pub')
    prik=os.getenv('API_pri')
    key = ts+prik+pubk
    hash = hashlib.md5(key.encode("utf-8")).hexdigest()
    print(hash)
    com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={winner}&ts={ts}&apikey={pubk}&hash={hash}')
    com_json=com.json()
    com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
    print(com_dumps)
    image = com_json['data']['results'][0]['images'][0]['path']
    print(image)
    image_path=(image+'/portrait_fantastic.jpg')
    print(image_path)
    book_title=com_json['data']['results'][0]['title']
    context={
        'comics':user.uploader.all,
        'current_user':user,
        'issues_total':Comic.objects.filter(uploaded_by=user).count(),
        'collections':Collection.objects.filter(user=user),
        'pic':image_path,
        'title':book_title
        }  
    return render(request, 'landing.html', context)

        
def alpha_landing(request):
    user=User.objects.get(id=request.session['user_id'])
    list=user.uploader.order_by('title')
    fav_lists=Comic.objects.values('title','upc', 'favorite')
    arr=[]
    for fav_list in fav_lists:
        if fav_list['favorite']!=None:
            arr.append(fav_list['upc'])
        else:
            print('crap')
    print(arr)
    count=Counter(arr)
    print(count)
    new=count.most_common()
    print(new)
    (j,_)=(new[0])
    winner=j
    print(winner)
    t = time.time()
    tr = round(t)
    ts = str(tr)
    pubk= os.getenv('API_pub')
    prik=os.getenv('API_pri')
    key = ts+prik+pubk
    hash = hashlib.md5(key.encode("utf-8")).hexdigest()
    print(hash)
    com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={winner}&ts={ts}&apikey={pubk}&hash={hash}')
    com_json=com.json()
    com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
    # print(com_dumps)
    image = com_json['data']['results'][0]['images'][0]['path']
    print(image)
    image_path=(image+'/portrait_fantastic.jpg')
    print(image_path)
    print(list)
    book_title=com_json['data']['results'][0]['title']
    context={
        'alpha_lists': list,
        'current_user':user,
        'issues_total':Comic.objects.filter(uploaded_by=user).count(),
        'collections':Collection.objects.filter(user=user),
        'pic':image_path,
        'title':book_title
    }
    return render(request, 'alpha_landing.html', context)

def rd_landing(request):
    user=User.objects.get(id=request.session['user_id'])
    list=user.uploader.order_by('release_date')
    fav_lists=Comic.objects.values('title','upc', 'favorite')
    arr=[]
    for fav_list in fav_lists:
        if fav_list['favorite']!=None:
            arr.append(fav_list['upc'])
        else:
            print('crap')
    print(arr)
    count=Counter(arr)
    print(count)
    new=count.most_common()
    print(new)
    (j,_)=(new[0])
    winner=j
    print(winner)
    t = time.time()
    tr = round(t)
    ts = str(tr)
    pubk= os.getenv('API_pub')
    prik=os.getenv('API_pri')
    key = ts+prik+pubk
    hash = hashlib.md5(key.encode("utf-8")).hexdigest()
    print(hash)
    com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={winner}&ts={ts}&apikey={pubk}&hash={hash}')
    com_json=com.json()
    com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
    # print(com_dumps)
    image = com_json['data']['results'][0]['images'][0]['path']
    print(image)
    image_path=(image+'/portrait_fantastic.jpg')
    print(image_path)
    print(list)
    print(list)
    book_title=com_json['data']['results'][0]['title']
    context={
        'rd_lists': list,
        'current_user':user,
        'issues_total':Comic.objects.filter(uploaded_by=user).count(),
        'collections':Collection.objects.filter(user=user),
        'pic':image_path,
        'title':book_title
    }
    return render(request, 'rd_landing.html', context)

def logout(request):
    request.session.flush()
    return redirect('/')

def comic_detail(request, comic_id):
        user=User.objects.get(id=request.session['user_id'])
        comic=Comic.objects.get(id=comic_id)
        t = time.time()
        tr = round(t)
        ts = str(tr)
        pubk= os.getenv('API_pub')
        prik=os.getenv('API_pri')        
        key = ts+prik+pubk
        hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        print(hash)
        book_upc=comic.upc
        print(book_upc)
        com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={book_upc}&ts={ts}&apikey={pubk}&hash={hash}')
        com_json=com.json()
        com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
        # print(com_dumps)
        q = com_json['data']['results'][0]['creators']['items']
        list = com_json['data']['results'][0]['creators']['items']
        image = com_json['data']['results'][0]['images'][0]['path']
        print(image)
        image_path=(image+'/portrait_uncanny.jpg')
        print(image_path)
        context={
            'this_user':user,
            'this_comic':comic,
            'creators':list,
            'collections':Collection.objects.filter(user=user),
            'img_path':image_path
        }  
        request.session['comic_id']=comic.id
        return render(request,'comic_detail.html', context)

def add_note(request, comic_id):
    to_update=Comic.objects.get(id=comic_id)
    to_update.notes=request.POST['note']
    to_update.save()
    return redirect(f'/{comic_id}/comic_detail')

def home(request):
    return redirect('/landing')

def add_fav(request, comic_id):
    x = comic_id
    this_comic=Comic.objects.get(id=x)
    user=User.objects.get(id=request.session['user_id'])
    user.a_fav.add(this_comic)
    print(this_comic.id)
    return redirect(f'/{comic_id}/comic_detail')

def un_fav(request, comic_id):
    x = comic_id
    this_comic=Comic.objects.get(id=x)
    user=User.objects.get(id=request.session['user_id'])
    user.a_fav.remove(this_comic)
    print(this_comic.id)
    return redirect(f'/{comic_id}/comic_detail')

def un_fav_fav_list(request, comic_id):
    x = comic_id
    this_comic=Comic.objects.get(id=x)
    user=User.objects.get(id=request.session['user_id'])
    user.a_fav.remove(this_comic)
    print(this_comic.id)
    return redirect('/fav_page')

def fav_page(request):
    user=User.objects.get(id=request.session['user_id'])
    context={
        'favorites': user.a_fav.all(),
        'total_favs': user.a_fav.all().count()
    }
    return render(request, 'fav_page.html', context)

def alpha_favs(request):
    user=User.objects.get(id=request.session['user_id'])
    context={
        'favorites': user.a_fav.all().order_by('title'),
        'total_favs': user.a_fav.all().count()
    }
    return render(request, 'alpha_favs.html', context)

def rd_fav_page(request):
    user=User.objects.get(id=request.session['user_id'])
    context={
        'favorites': user.a_fav.all().order_by('release_date'),
        'total_favs': user.a_fav.all().count()
    }
    return render(request, 'rd_fav_page.html', context)

def add_collection(request):
    if request.method=='POST':
        errors = Collection.objects.collection_validator(request.POST)
    if len(errors) != 0:
        for k, v in errors.items():
            messages.error(request, v)
        return redirect('/landing')
    else:
        this_user=User.objects.get(id=request.session['user_id'])
        new_col=Collection.objects.create(
            user=this_user,
            col_name=request.POST['new_col_name']
            )
        return redirect('/landing')

def add_to_collection(request, collection_id):
    # col_id=collection_id
    comic=Comic.objects.get(id=request.session['comic_id'])
    # collection = Collection.objects.get(id=col_id)
    collection = Collection.objects.get(id=collection_id)
    collection.comic.add(comic)
    request.session['collection_id']=collection_id
    return redirect(f"/{comic.id}/comic_detail")

def collection_detail(request, collection_id):
    collection=Collection.objects.get(id=collection_id)
    user=User.objects.get(id=request.session['user_id'])
    # collection=Collection.objects.get(id=request.session['collection_id'])
    context={
        'issues': collection.comic.all(),
        'total_issues': collection.comic.all().count(),
        'this_collection':collection
    }
    request.session['col_id']=collection_id
    return render(request, 'collection_detail.html', context)

def alpha_collection_detail(request, collection_id):
    collection=Collection.objects.get(id=collection_id)
    user=User.objects.get(id=request.session['user_id'])
    # collection=Collection.objects.get(id=request.session['col_id'])
    context={
        'issues': collection.comic.all().order_by('title'),
        'total_issues': collection.comic.all().count(),
        'this_collection':collection
    }
    request.session['col_id']=collection_id
    return render(request, 'alpha_collection_detail.html', context)

def rd_collection_detail(request, collection_id):
    collection=Collection.objects.get(id=collection_id)
    user=User.objects.get(id=request.session['user_id'])
    # collection=Collection.objects.get(id=request.session['col_id'])
    context={
        'issues': collection.comic.all().order_by('release_date'),
        'total_issues': collection.comic.all().count(),
        'this_collection':collection
    }
    request.session['col_id']=collection_id
    return render(request, 'rd_collection_detail.html', context)

def un_to_collection(request, collection_id):
    col_id=collection_id
    comic=Comic.objects.get(id=request.session['comic_id'])
    collection = Collection.objects.get(id=col_id)
    collection.comic.remove(comic)
    return redirect(f"/{comic.id}/comic_detail")

def un_to_collection_in_collection(request, comic_id):
    coll_id=request.session['col_id']
    comic=Comic.objects.get(id=comic_id)
    print(comic)
    collection = Collection.objects.get(id=coll_id)
    collection.comic.remove(comic)
    return redirect(f'/{coll_id}/collection_detail')

def collection_edit(request, collection_id):
    collection=Collection.objects.get(id=collection_id)
    user=User.objects.get(id=request.session['user_id'])
    context={
        'issues': collection.comic.all(),
        'total_issues': collection.comic.all().count(),
        'this_collection':collection
    }
    return render(request, 'collection_edit.html', context)

def update_collection_name(request, collection_id):
    if request.method=='POST':
        errors = Collection.objects.collection_validator(request.POST)
    if len(errors) != 0:
        for k, v in errors.items():
            messages.error(request, v)
        return redirect(f"/{collection_id}/collection_edit")
    else:
        to_update=Collection.objects.get(id=collection_id)
        to_update.col_name=request.POST['new_col_name']
        to_update.save()
        return redirect(f"/{collection_id}/collection_edit")

def del_collection(request, collection_id):
    collection=Collection.objects.get(id=collection_id)
    context={
        'this_collection':collection
    }
    request.session['col_to_delete']=collection_id
    return render(request, 'delete_conf.html', context)

def delete_conf(request):
        to_delete=Collection.objects.get(id=request.session['col_to_delete'])
        to_delete.delete()
        return redirect('/landing')
    
def del_comic(request, comic_id):
    comic=Comic.objects.get(id=comic_id)
    context={
        'this_comic':comic
    }
    request.session['comic_to_delete']=comic_id
    return render(request, 'delete_conf_comic.html', context)

def del_conf_comic(request):
        to_delete=Comic.objects.get(id=request.session['comic_to_delete'])
        to_delete.delete()
        return redirect('/landing')

def most_fav(request):
    lists=Comic.objects.values('title','upc', 'favorite')
    fav_arr=[]
    for list in lists:
        if list['favorite']!=None:
            fav_arr.append(list['upc'])
            # print(list)
            # print(list['title'])
            # print(list['favorite'])
            # print(list['upc'])
        else:
            print('crap')
    count=Counter(fav_arr)
    print(count)
    fav=next(iter(count))
    print(fav)

    return redirect ('/landing')

def test(request):
    lists=Comic.objects.values('title','upc', 'favorite')
    arr=[]
    for list in lists:
        if list['favorite']!=None:
            arr.append(list['upc'])
        else:
            print('crap')
    print(arr)
    count=Counter(arr)
    print(count)
    new=count.most_common()
    print(new)
    (j,_)=(new[0])
    winner=j
    print(winner)
    t = time.time()
    tr = round(t)
    ts = str(tr)
    pubk= os.getenv('API_pub')
    prik=os.getenv('API_pri')
    key = ts+prik+pubk
    hash = hashlib.md5(key.encode("utf-8")).hexdigest()
    print(hash)
    com = requests.get(f'https://gateway.marvel.com:443/v1/public/comics?&upc={winner}&ts={ts}&apikey={pubk}&hash={hash}')
    com_json=com.json()
    com_dumps=json.dumps(com_json,sort_keys=True,indent=4)
    # print(com_dumps)
    image = com_json['data']['results'][0]['images'][0]['path']
    print(image)
    image_path=(image+'/portrait_fantastic.jpg')
    print(image_path)


    return render (request,'test.html')
