# Like/Dislike System + Profile Page for Flask

## Like Model
```python
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    like_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'article_id'),)
```

## Toggle route pattern
```python
@main_bp.route('/like/<int:article_id>', methods=['POST'])
@login_required
def toggle_like(article_id):
    article = Article.query.get_or_404(article_id)
    like_type = request.form.get('type', 'like')
    existing = Like.query.filter_by(user_id=current_user.id, article_id=article_id).first()

    if existing:
        if existing.like_type == like_type:
            db.session.delete(existing)      # toggle off
        else:
            existing.like_type = like_type    # switch like↔dislike
    else:
        db.session.add(Like(user_id=current_user.id, article_id=article_id, like_type=like_type))

    db.session.commit()
    return redirect(url_for('main.article', slug=article.slug))
```

## Article helper methods
```python
class Article(db.Model):
    # ...
    def get_likes(self):
        return Like.query.filter_by(article_id=self.id, like_type='like').count()
    def get_dislikes(self):
        return Like.query.filter_by(article_id=self.id, like_type='dislike').count()
```

## Profile page pattern
- Tabs: Published articles | Recent comments | Liked articles
- Stats card: article count, comment count, like count
- Edit profile: bio + avatar_url (URL input, no file upload needed)
- Route: `/profile/<username>`

## Template like button (Bootstrap)
```html
<form method="post" action="{{ url_for('main.toggle_like', article_id=article.id) }}">
    <input type="hidden" name="type" value="like">
    <button class="btn btn-sm {{ 'btn-success' if user_like and user_like.like_type == 'like' else 'btn-outline-success' }}">
        <i class="bi bi-hand-thumbs-up-fill"></i> {{ article.get_likes() }}
    </button>
</form>
```
