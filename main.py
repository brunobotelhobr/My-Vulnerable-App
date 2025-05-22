# Standard library imports
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.responses import RedirectResponse

# Security configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # Em produção, use uma chave secreta segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app initialization
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root route redirect
@app.get("/")
async def root():
    return RedirectResponse(url="/home.html")

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, index=True)


# Pydantic Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    name: str
    content: str
    created_at: datetime
    product_id: int

    class Config:
        from_attributes = True


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class CartItem(BaseModel):
    product_id: int
    quantity: int


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Database utilities
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_products():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    
    # Add sample products if table is empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        products = [
            ('Professional Fishing Rod', 
             'High-end carbon fiber fishing rod with perfect balance', 
             299.99, 'Rods'),
            ('Premium Fishing Reel', 
             'High-performance spinning reel with 10 ball bearings', 
             199.99, 'Reels'),
            ('Tackle Box Set', 
             'Complete set of fishing lures, hooks, and accessories', 
             89.99, 'Accessories'),
            ('Fishing Line 500m', 
             'Strong monofilament fishing line, 20lb test', 
             24.99, 'Lines'),
            ('Fish Finder GPS', 
             'Advanced sonar fish finder with GPS navigation', 
             499.99, 'Electronics'),
            ('Fishing Vest', 
             'Multi-pocket fishing vest for all your gear', 
             79.99, 'Apparel'),
            ('Bait Cast Net', 
             'Professional grade cast net for catching live bait', 
             45.99, 'Nets'),
            ('Fishing Hooks Set', 
             'Set of 100 high-carbon steel hooks in various sizes', 
             29.99, 'Hooks'),
            ('Fishing Chair', 
             'Comfortable folding chair with rod holders', 
             69.99, 'Accessories'),
            ('Fishing Cooler', 
             '25L cooler perfect for keeping your catch fresh', 
             129.99, 'Accessories')
        ]
        c.executemany('''
            INSERT INTO products (name, description, price, category) 
            VALUES (?, ?, ?, ?)
        ''', products)
    
    conn.commit()
    conn.close()


def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')
    
    # Create user_addresses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            country TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT
        )
    ''')
    
    # Create comments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            product_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Create cart table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    init_products()


# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None or user.id != user_id:
        raise credentials_exception
    return user


# Authentication endpoints
@app.post("/register", response_model=UserBase)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserBase(username=db_user.username)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id
        }, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Product endpoints
@app.get("/products/search")
async def search_products(q: str = '', skip: int = 0, limit: int = 10):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    # SQL injection vulnerability for educational purposes
    query = f"""
        SELECT * FROM products 
        WHERE name LIKE '%{q}%' 
        LIMIT {limit} OFFSET {skip}
    """
    c.execute(query)
    rows = c.fetchall()
    
    return [
        {
            "id": row[0], 
            "name": row[1], 
            "description": row[2],
            "price": row[3], 
            "category": row[4]
        } 
        for row in rows
    ]


# Comment endpoints
@app.post("/comments/", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_comment = Comment(
        name=current_user.username,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@app.get("/comments/", response_model=list[CommentResponse])
async def get_comments(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comments = db.query(Comment).offset(skip).limit(limit).all()
    return comments


@app.get("/products/{product_id}/comments")
async def get_product_comments(
    product_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comments = (
        db.query(Comment)
        .filter(Comment.product_id == product_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments


@app.post("/products/{product_id}/comments")
async def create_product_comment(
    product_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_comment = Comment(
        name=current_user.username,
        content=comment.content,
        product_id=product_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


# Cart endpoints
@app.post("/api/cart/add")
async def add_to_cart(
    item: CartItem, 
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        # Check if product exists
        c.execute('SELECT * FROM products WHERE id = ?', (item.product_id,))
        product = c.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already in cart
        c.execute('''
            SELECT * FROM cart 
            WHERE user_id = ? AND product_id = ?
        ''', (current_user.id, item.product_id))
        cart_item = c.fetchone()
        
        if cart_item:
            # Update quantity
            c.execute('''
                UPDATE cart 
                SET quantity = quantity + ?
                WHERE user_id = ? AND product_id = ?
            ''', (item.quantity, current_user.id, item.product_id))
        else:
            # Add new item
            c.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            ''', (current_user.id, item.product_id, item.quantity))
        
        conn.commit()
        
        # Get updated cart count
        c.execute(
            'SELECT SUM(quantity) as count FROM cart WHERE user_id = ?', 
            (current_user.id,)
        )
        result = c.fetchone()
        cart_count = result['count'] or 0
        
        return {"message": "Item added to cart", "cart_count": cart_count}
    
    finally:
        conn.close()


@app.get("/api/cart/count")
async def get_cart_count(current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute(
            'SELECT SUM(quantity) as count FROM cart WHERE user_id = ?', 
            (current_user.id,)
        )
        result = c.fetchone()
        return {"count": result['count'] or 0}
    
    finally:
        conn.close()


@app.get("/api/cart")
async def get_cart(current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT c.*, p.name, p.price, p.description
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (current_user.id,))
        
        cart_items = []
        for row in c.fetchall():
            cart_items.append({
                "id": row['id'],
                "product_id": row['product_id'],
                "quantity": row['quantity'],
                "name": row['name'],
                "price": row['price'],
                "description": row['description'],
                "total": row['price'] * row['quantity']
            })
        
        return cart_items
    
    finally:
        conn.close()


@app.delete("/api/cart/{item_id}")
async def remove_from_cart(
    item_id: int, 
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute('''
            DELETE FROM cart 
            WHERE id = ? AND user_id = ?
        ''', (item_id, current_user.id))
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        conn.commit()
        return {"message": "Item removed from cart"}
    
    finally:
        conn.close()


@app.put("/api/cart/{item_id}")
async def update_cart_item(
    item_id: int, 
    quantity: int = Query(..., gt=0),  # Usando Query para receber da query string, garantindo que seja maior que 0
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        # Check if item exists and belongs to user
        c.execute('''
            SELECT * FROM cart 
            WHERE id = ? AND user_id = ?
        ''', (item_id, current_user.id))
        cart_item = c.fetchone()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Update quantity
        c.execute('''
            UPDATE cart 
            SET quantity = ?
            WHERE id = ? AND user_id = ?
        ''', (quantity, item_id, current_user.id))
        
        conn.commit()
        return {"message": "Quantity updated successfully"}
    
    finally:
        conn.close()


# User profile endpoints
@app.put("/api/user/{user_id}/address")
async def update_address(
    user_id: int,
    address: Address, 
    current_user: User = Depends(get_current_user)
):
    # # Verify if the user is updating their own address
    # if current_user.id != user_id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Not authorized to update this address"
    #     )

    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    try:
        # Check if user has an address
        c.execute(
            'SELECT * FROM user_addresses WHERE user_id = ?', 
            (user_id,)
        )
        existing_address = c.fetchone()
        
        if existing_address:
            # Update existing address
            c.execute('''
                UPDATE user_addresses 
                SET street = ?, city = ?, state = ?, postal_code = ?, country = ?
                WHERE user_id = ?
            ''', (
                address.street, address.city, address.state,
                address.zip_code, address.country, user_id
            ))
        else:
            # Create new address
            c.execute('''
                INSERT INTO user_addresses (
                    user_id, street, city, state, postal_code, country
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id, address.street, address.city,
                address.state, address.zip_code, address.country
            ))
        
        conn.commit()
        return {"message": "Address updated successfully"}
    
    finally:
        conn.close()


@app.get("/api/user/{user_id}/address")
async def get_address(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # # Verify if the user is getting their own address
    # if current_user.id != user_id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Not authorized to view this address"
    #     )

    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute(
            'SELECT * FROM user_addresses WHERE user_id = ?', 
            (user_id,)
        )
        address = c.fetchone()
        
        if not address:
            return None
        
        return {
            "street": address['street'],
            "city": address['city'],
            "state": address['state'],
            "zip_code": address['postal_code'],
            "country": address['country']
        }
    
    finally:
        conn.close()


@app.put("/api/user/password")
async def change_password(
    password_change: PasswordChange, 
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    try:
        # Verify current password
        current_hash = hashlib.sha256(
            password_change.current_password.encode()
        ).hexdigest()
        
        if current_hash != current_user.hashed_password:
            raise HTTPException(
                status_code=400, 
                detail="Current password is incorrect"
            )
        
        # Update password
        new_hash = hashlib.sha256(
            password_change.new_password.encode()
        ).hexdigest()
        
        c.execute(
            'UPDATE users SET hashed_password = ? WHERE id = ?',
            (new_hash, current_user.id)
        )
        
        conn.commit()
        return {"message": "Password updated successfully"}
    
    finally:
        conn.close()


# Initialize database
Base.metadata.create_all(bind=engine)
init_db()

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static") 