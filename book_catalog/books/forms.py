# 6. forms.py 表单代码
"""
books/forms.py
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Book, Category, Author, Tag
from .models import Book, Author, AuthorProfile
from datetime import date

class BookForm(forms.ModelForm):
    """添加图书的表单，包含数据验证"""
    # 添加一个文本字段用于输入作者名称
    author_name = forms.CharField(
        label='Author Name',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter author name'
        })
    )
    class Meta:
        model = Book
        fields = ['title', 'subtitle', 'isbn', 'price', 'pages', 
                  'publication_date', 'is_bestseller', 'is_in_stock',
                  'language', 'description', 'cover_image', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Please enter the title of the book'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subtitle (optional)'}),
            'isbn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '978-7-xxxx-xxxx-x'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'pages': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Number of pages'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Introduction to the book...'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-file'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'is_bestseller': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_in_stock': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    def save(self, commit=True):
        book = super().save(commit=False)
        
        # 处理作者
        author_name = self.cleaned_data.get('Author name')
        if author_name:
            # 查找或创建作者
            author, created = Author.objects.get_or_create(
                name=author_name,
                defaults={
                    'gender': 'O',  # Other
                    'nationality': 'Unknown'
                }
            )
            if created:
                # 为作者创建默认的 profile
                AuthorProfile.objects.get_or_create(
                    author=author,
                    defaults={
                        'bio': f'Author of "{book.title}"',
                        'birth_place': 'Unknown'
                    }
                )
            book.author = author
        else:
            # 如果没有提供作者名，设置为匿名作者
            anonymous, _ = Author.objects.get_or_create(
                name='Anonymous',
                defaults={'gender': 'O', 'nationality': 'Unknown'}
            )
            book.author = anonymous
        
        if commit:
            book.save()
            self.save_m2m()
        
        return book
    def clean_price(self):
        """验证价格：必须大于0"""
        price = self.cleaned_data.get('Price')
        if price and price <= 0:
            raise ValidationError('The price must be greater than 0')
        if price and price > 100000:
            raise ValidationError('The price cannot exceed 10,0000')
        return price
    
    def clean_pages(self):
        """验证页数：必须在1-5000之间"""
        pages = self.cleaned_data.get('Pages')
        if pages and pages < 1:
            raise ValidationError('The number of pages is at least 1 page')
        if pages and pages > 5000:
            raise ValidationError('The number of pages cannot exceed 5000 pages')
        return pages
    
    def clean_isbn(self):
        """验证ISBN：基本格式检查"""
        isbn = self.cleaned_data.get('ISBN')
        if isbn:
            # 简单验证：清除分隔符后检查长度
            isbn_clean = isbn.replace('-', '').replace(' ', '')
            if len(isbn_clean) not in [10, 13]:
                raise ValidationError('ISBN must be 10 or 13 digits (can contain hyphens)')
        return isbn
    
    def clean_publication_date(self):
        """验证出版日期：不能晚于今天"""
        pub_date = self.cleaned_data.get('Publication date')
        if pub_date and pub_date > date.today():
            raise ValidationError('The publication date cannot be later than today')
        return pub_date
    
    def clean(self):
        """跨字段验证"""
        cleaned_data = super().clean()
        # 可以添加更多跨字段验证逻辑
        return cleaned_data