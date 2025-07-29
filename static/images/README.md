# Logo Klasörü

Bu klasöre logonuzu koyabilirsiniz.

## Önerilen Logo Dosyaları:

- `logo.png` - Ana logo (40x40px)
- `logo-large.png` - Büyük logo (200x200px) 
- `favicon.ico` - Browser ikonu (16x16px)

## Kullanım:

```html
<!-- Navbar'da -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo" class="logo-img">

<!-- Hero section'da -->
<img src="{{ url_for('static', filename='images/logo-large.png') }}" alt="Logo" class="hero-logo">
```

## CSS Örnekleri:

```css
.logo-img {
    width: 40px;
    height: 40px;
    object-fit: contain;
    border-radius: 8px;
}

.hero-logo {
    width: 100px;
    height: 100px;
    margin-bottom: 20px;
}
```
