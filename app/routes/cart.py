import pickle
import base64
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.models import User, Cart, Product
from app.schemas.schemas import CartItem

router = APIRouter()


@router.post("/api/cart/add")
async def add_to_cart(
    item: CartItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to user's cart."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already in cart
    cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == item.product_id
    ).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += item.quantity
    else:
        # Add new item
        cart_item = Cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    
    # Get updated cart count
    cart_count = db.query(Cart.quantity).filter(
        Cart.user_id == current_user.id
    ).all()
    total_count = sum(count[0] for count in cart_count)
    
    return {"message": "Item added to cart", "cart_count": total_count}


@router.get("/api/cart/count")
async def get_cart_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the total number of items in user's cart."""
    cart_count = db.query(Cart.quantity).filter(
        Cart.user_id == current_user.id
    ).all()
    return {"count": sum(count[0] for count in cart_count)}


@router.get("/api/cart")
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items in user's cart with product details."""
    cart_items = db.query(Cart, Product).join(
        Product, Cart.product_id == Product.id
    ).filter(Cart.user_id == current_user.id).all()
    
    return [
        {
            "id": item.Cart.id,
            "product_id": item.Cart.product_id,
            "quantity": item.Cart.quantity,
            "name": item.Product.name,
            "price": item.Product.price,
            "description": item.Product.description,
            "total": item.Product.price * item.Cart.quantity
        }
        for item in cart_items
    ]


@router.delete("/api/cart/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from user's cart."""
    cart_item = db.query(Cart).filter(
        Cart.id == item_id,
        Cart.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart"}


@router.put("/api/cart/{item_id}")
async def update_cart_item(
    item_id: int,
    quantity: int = Query(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the quantity of an item in user's cart."""
    cart_item = db.query(Cart).filter(
        Cart.id == item_id,
        Cart.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    cart_item.quantity = quantity
    db.commit()
    
    return {"message": "Quantity updated successfully"}


@router.get("/api/cart/export")
async def export_cart_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export cart data in pickle format (base64 encoded) - Vulnerable to RCE."""
    cart_items = db.query(Cart, Product).join(
        Product, Cart.product_id == Product.id
    ).filter(Cart.user_id == current_user.id).all()
    
    cart_data = {
        'user_id': current_user.id,
        'items': [{
            'product_id': item.Cart.product_id,
            'quantity': item.Cart.quantity,
            'name': item.Product.name,
            'description': item.Product.description,
            'price': item.Product.price
        } for item in cart_items]
    }
    
    # Vulnerable to RCE through pickle
    serialized = pickle.dumps(cart_data)
    encoded = base64.b64encode(serialized).decode()
    
    return {"cart_data": encoded}


@router.post("/api/cart/import")
async def import_cart_data(
    cart_data: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import cart data from pickle format (base64 encoded) - Vulnerable to RCE."""
    try:
        # WARNING: Intentionally vulnerable to RCE
        decoded = base64.b64decode(cart_data)
        cart_data = pickle.loads(decoded)  # Vulnerable to RCE
        
        # Clear current cart
        db.query(Cart).filter(Cart.user_id == current_user.id).delete()
        
        # Import cart items
        for item in cart_data['items']:
            db.add(Cart(
                user_id=current_user.id,
                product_id=item['product_id'],
                quantity=item['quantity']
            ))
        
        db.commit()
        return {"message": "Cart data imported successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cart data: {str(e)}"
        ) 