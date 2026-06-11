# 模型选项（可选，影响Admin后台）
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Category(models.Model):
    """图书分类 - 一对多关系（一个分类包含多本图书）"""
    name = models.CharField('Category Name', max_length=50, unique=True)
    description = models.TextField('Description', blank=True)
    created_at = models.DateTimeField('Creation time', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AuthorProfile(models.Model):
    """作者详情 - 一对一关系（与Author关联）"""
    bio = models.TextField('Personal profile', blank=True)
    birth_place = models.CharField('Place of birth', max_length=100, blank=True)
    website = models.URLField('Personal website', blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    class Meta:
        verbose_name = 'Author profile'
        verbose_name_plural = 'Author profile'
    
    def __str__(self):
        if hasattr(self, 'author') and self.author:
            return f"The profile of {self.author.name}"
        return f"Details of unaffiliated authors (ID: {self.id})"

class Author(models.Model):
    """作者模型 - 一对多关系（一个作者可写多本书）"""
    class Gender(models.TextChoices):
        MALE = 'M', 'male'
        FEMALE = 'F', 'female'
        OTHER = 'O', 'other'
    
    name = models.CharField('name', max_length=50)
    gender = models.CharField('gender', max_length=1, choices=Gender.choices, default=Gender.OTHER)
    birth_date = models.DateField('Date of birth', null=True, blank=True)
    nationality = models.CharField('nationality', max_length=50, blank=True)
    profile = models.OneToOneField(AuthorProfile, on_delete=models.CASCADE, 
                                   verbose_name='Author profile', null=True, blank=True, related_name='author')
    
    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Author'
        ordering = ['name']
    
    def __str__(self):
        if self.nationality:
            return f"{self.name} ({self.nationality})"
        return self.name

class Tag(models.Model):
    """标签模型 - 多对多关系（与Book关联）"""
    name = models.CharField('The name of the tag', max_length=30, unique=True)
    color = models.CharField('The color of the label', max_length=7, default='#6c5ce7')
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tag'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Book(models.Model):
    """图书核心模型"""
    # 基础字段
    title = models.CharField('Title', max_length=200)
    subtitle = models.CharField('Subtitle', max_length=200, blank=True)
    isbn = models.CharField('ISBN', max_length=13, unique=False, blank=True, null=True)
    
    # 数字字段
    price = models.DecimalField('Price', max_digits=8, decimal_places=2, 
                                 validators=[MinValueValidator(0)])
    pages = models.IntegerField('Pages', validators=[MinValueValidator(1)], default=100)
    
    # 日期字段
    publication_date = models.DateField('Publication date', default=date.today)
    
    # 布尔值字段
    is_bestseller = models.BooleanField('Bestseller', default=False)
    is_in_stock = models.BooleanField('In stock', default=True)
    
    # 枚举类型 - 通过choices实现
    class Language(models.TextChoices):
        CHINESE = 'ZH', 'Chinese'
        ENGLISH = 'EN', 'English'
        JAPANESE = 'RU', 'Russian'
        OTHER = 'OT', '其他'
    
    language = models.CharField('Language', max_length=2, choices=Language.choices, default=Language.CHINESE)
    
    # 文本字段
    description = models.TextField('Book introduction', blank=True)
    cover_image = models.ImageField('Cover image', upload_to='covers/', blank=True, null=True)
    
    # 外键关系：一对多（一个分类对应多本图书）
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                                 related_name='books', verbose_name='Category')
    
    # 外键关系：一对多（一个作者对应多本图书）
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True,
                               related_name='books', verbose_name='Author')
    
    # 多对多关系（一本图书可以有多个标签）
    tags = models.ManyToManyField(Tag, blank=True, related_name='books', verbose_name='Tags')
    
    class Meta:
        verbose_name = 'books'
        verbose_name_plural = 'books'
        ordering = ['-publication_date']
        # 添加约束：只对非空的ISBN检查唯一性
        constraints = [
            models.UniqueConstraint(
                fields=['isbn'],
                condition=models.Q(isbn__isnull=False),
                name='unique_isbn_not_null'
            )
        ]
    
    def __str__(self):
        return self.title
