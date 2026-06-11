from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import models
from .models import Book, Category, Author, Tag
from .forms import BookForm

def home(request):
    """首页视图"""
    # 统计数据
    total_books = Book.objects.count()
    total_categories = Category.objects.count()
    total_authors = Author.objects.count()
    bestsellers = Book.objects.filter(is_bestseller=True).count()
    
    # 最近添加的5本书
    recent_books = Book.objects.all()[:5]
    
    # 热门分类（包含图书最多的3个分类）
    popular_categories = Category.objects.annotate(
        book_count=models.Count('books')
    ).order_by('-book_count')[:3]
    
    context = {
        'total_books': total_books,
        'total_categories': total_categories,
        'total_authors': total_authors,
        'bestsellers': bestsellers,
        'recent_books': recent_books,
        'popular_categories': popular_categories,
    }
    return render(request, 'books/home.html', context)

def book_list(request):
    """图书列表页 - 网格展示所有图书"""
    books = Book.objects.select_related('category', 'author').prefetch_related('tags').all()
    categories = Category.objects.all()
    
    # 分类筛选
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)
    
    context = {
        'books': books,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, id):
    """图书详情页"""
    book = get_object_or_404(
        Book.objects.select_related('category', 'author', 'author__profile'), 
        id=id
    )
    context = {'book': book}
    return render(request, 'books/book_detail.html', context)

def book_add(request):
    """添加图书表单页"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{form.cleaned_data["title"]}" added successfully!')
            return redirect('books:book_list')
        else:
            # 显示错误信息
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = BookForm()
    
    return render(request, 'books/book_form.html', {'form': form})

def book_delete(request, id):
    """删除图书功能（带确认）"""
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" has been successfully deleted.')
        return redirect('books:book_list')
    
    return render(request, 'books/book_confirm_delete.html', {'book': book})
