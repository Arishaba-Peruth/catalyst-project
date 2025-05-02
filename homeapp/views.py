from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.contrib.auth import authenticate, login, logout
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
# view for welcoming page
def index(request):
    return render(request, 'homeapp/index.html')

# view for allstock page
@login_required
def allstock(request):
    stocks = Stock.objects.all().order_by('-id')
    return render(request, 'homeapp/allstock.html', {'stocks': stocks})

# view for stock detail Page
@login_required
def stock_detail(request, stock_id):
    stock = Stock.objects.get(id=stock_id)
    return render(request, 'homeapp/stockdetail.html', {'stock': stock})

@login_required
def sell_item(request, pk):
    # creating a variable sell_item and accessing all entries in the Stock model by there primary keys
    sell_item = Stock.objects.get(id=pk)

    # accessing our form from forms.py
    sales_form = AddSaleForm(request.POST)
    if request.method == 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.Name_of_produce = sell_item  # Set the foreign key to the Stock item
            new_sale.item_name = sell_item.Name_of_produce  # Set the item name from the stock
            
            # Get the quantity being sold
            issued_quantity = int(request.POST['Tonnage_in_kgs'])
            
            # Check if we have enough stock
            if issued_quantity <= sell_item.Tonnage_in_kgs:
                # Update the stock quantity by subtracting the sold amount
                sell_item.Tonnage_in_kgs -= issued_quantity
                sell_item.total_quantity = issued_quantity
                sell_item.save()
                
                # Save the sale
                new_sale.save()
                
                return redirect('receipt')
            else:
                # If not enough stock, add an error to the form
                sales_form.add_error('Tonnage_in_kgs', 'Not enough stock available')
                
    return render(request, 'homeapp/sell_item.html', {'sales_form': sales_form})

@login_required
def receipt(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'homeapp/receipt.html', {'sales': sales})

def Login(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_director:
                return redirect('director')
            elif user.is_manager:
                return redirect('manager')
            elif user.is_salesagent:
                return redirect('salesagent')
            else:
                messages.error(request, "Invalid user role")
        else:
            messages.error(request, "Invalid username or password")
                    
    return render(request, 'homeapp/login.html')

# view for signup page
def signup(request):
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            return redirect('/login')
    else:
        form = UserCreation()
    
    return render(request, 'homeapp/signup.html', {'form': form})

@login_required
def allsales(request):
    sales = Sale.objects.all().order_by('-id')
    stocks = Stock.objects.all()  # Get all stocks to choose from
    context = {
        'sales': sales,
        'stocks': stocks  # Pass stocks to template
    }
    return render(request, 'homeapp/allsales.html', context) 

@login_required
def addstock(request, pk):
    sold_item = Stock.objects.get(id=pk)
    form = UpdateStockForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            added_quantity = int(request.POST['received_quantity'])
            sold_item.Tonnage_in_kgs += added_quantity
            sold_item.save()

            print(added_quantity)
            print(sold_item.Tonnage_in_kgs)
            return redirect('allstock')

    return render(request, 'homeapp/addstock.html', {'form': form})

@login_required
def addsales(request, pk):
    # Use get_object_or_404 to handle non-existent objects gracefully
    sell_item = get_object_or_404(Stock, id=pk)

    # Initialize form with POST data if POST request, otherwise empty form
    sales_form = AddSaleForm(request.POST if request.method == 'POST' else None)
    
    if request.method == 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.item_name = sell_item
            new_sale.unit_price = sell_item.Unit_price
            
            # Get the quantity being sold
            issued_quantity = int(request.POST['Tonnage_in_kgs'])
            
            # Check if we have enough stock
            if issued_quantity <= sell_item.Tonnage_in_kgs:
                # Update the stock quantity by subtracting the sold amount
                sell_item.Tonnage_in_kgs -= issued_quantity
                sell_item.total_quantity = issued_quantity
                sell_item.save()
                
                # Save the sale
                new_sale.save()
                
                return redirect('allsales')
            else:
                # If not enough stock, add an error to the form
                sales_form.add_error('Tonnage_in_kgs', 'Not enough stock available')
    
    context = {
        'sales_form': sales_form,
        'sell_item': sell_item,  # Pass the item being sold to the template
    }        
    return render(request, 'homeapp/addsales.html', context)
            
@login_required
def deferredpayment(request):
    deferred_payments = Deferred_Payment.objects.all().order_by('-Due_date')
    return render(request, 'homeapp/deferredpayment.html', {'deferred_payments': deferred_payments})

@login_required
def add_deferredpayment(request):
    if request.method == 'POST':
        form = AddDeferred_PaymentForm(request.POST)
        if form.is_valid():
            deferred_payment = form.save(commit=False)
            deferred_payment.save()
            return redirect('deferredpayment')
    else:
        form = AddDeferred_PaymentForm()
    
    stocks = Stock.objects.all()
    branches = Branch.objects.all()
    context = {
        'form': form,
        'stocks': stocks,
        'branches': branches,
    }
    return render(request, 'homeapp/add_deferredpay.html', context)

# view for editpage
@login_required
def editsalespage(request, pk):
    tx_to_edit = Sale.objects.get(pk=pk)
    if request.method == 'POST':
        data = request.POST
        edited_produce_name = data.get('Name_of_produce')
        edited_item_name = data.get('item_name')
        edited_tonnage = data.get('Tonnage_in_kgs')
        edited_amount_paid = data.get('Amount_paid')
        edited_sales_agent = data.get('Sales_agent_name')
        edited_buyer_name = data.get('Name_of_buyer')
        edited_payment_method = data.get('method_of_payment')
        
        stock_id = data.get('Name_of_produce')
        stock_instance = get_object_or_404(Stock, pk=stock_id)
        
        tx_to_edit.Name_of_produce = stock_instance
        tx_to_edit.item_name = edited_item_name
        tx_to_edit.Tonnage_in_kgs = edited_tonnage
        tx_to_edit.Amount_paid = edited_amount_paid
        tx_to_edit.Sales_agent_name = edited_sales_agent
        tx_to_edit.Name_of_buyer = edited_buyer_name
        tx_to_edit.method_of_payment = edited_payment_method
        tx_to_edit.save()
        return redirect('/view/' + str(tx_to_edit.pk))
    
    context = {
        "edit_details": tx_to_edit,
        "stock_list": Stock.objects.all()
    }
    return render(request, 'homeapp/edit.html', context)

@login_required
def viewpage(request, pk):
    database_id = pk
    tx = Sale.objects.get(pk=database_id)
    context = {
        "details": tx
    }
    return render(request, 'homeapp/view.html', context)

@login_required
def deteletransaction(request, pk):
    to_delete = Sale.objects.get(pk=pk)
    if request.method == 'POST':
        data = request.POST
        to_delete.delete()
        return redirect('/')
    
    context = {
        "details": to_delete
    }
    return render(request, 'homeapp/delete.html', context)

@login_required
def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'homeapp/receipt_detail.html', {'receipt': receipt})

@login_required
def manager(request):
    if not request.user.is_manager:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Get all stock items grouped by product name
    all_stocks = Stock.objects.all()
    
    # Create a dictionary to group stocks by product name
    grouped_stocks = {}
    for stock in all_stocks:
        if stock.Name_of_produce not in grouped_stocks:
            grouped_stocks[stock.Name_of_produce] = {
                'name': stock.Name_of_produce,
                'branches': {},
                'total_quantity': 0
            }
        
        branch_name = stock.Branch.branch_name if stock.Branch else 'Unassigned'
        if branch_name not in grouped_stocks[stock.Name_of_produce]['branches']:
            grouped_stocks[stock.Name_of_produce]['branches'][branch_name] = 0
        grouped_stocks[stock.Name_of_produce]['branches'][branch_name] += stock.Tonnage_in_kgs
        grouped_stocks[stock.Name_of_produce]['total_quantity'] += stock.Tonnage_in_kgs
    
    # Convert dictionary to list for template
    combined_stocks = list(grouped_stocks.values())
    
    # Get recent sales, limited to last 10
    recent_sales = Sale.objects.all().order_by('-Date_time')[:10]
    
    # Get low stock items (less than 100kg)
    low_stock_items = Stock.objects.filter(Tonnage_in_kgs__lt=100)
    
    context = {
        'combined_stocks': combined_stocks,
        'recent_sales': recent_sales,
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'homeapp/dashboard1.html', context)

@login_required
def viewcredit(request, pk):
    credit = Deferred_Payment.objects.get(pk=pk)
    context = {
        "creditdetails": credit
    }
    return render(request, 'homeapp/viewcredit.html', context)

@login_required
def editcredit(request, pk):
    credit_to_edit = Deferred_Payment.objects.get(pk=pk)
    if request.method == 'POST':
        data = request.POST
        contact = data.get('Contact')
        if not contact:
            return render(request, 'homeapp/editcredit.html', {
                'edit_credit': credit_to_edit,
                'error': 'Contact number is required'
            })
        
        credit_to_edit.Name_of_buyer = data.get('Name_of_buyer')
        credit_to_edit.Nin = data.get('Nin')
        credit_to_edit.Location = data.get('Location')
        credit_to_edit.Amount_due = data.get('Amount_due')
        credit_to_edit.Contact = int(contact)
        credit_to_edit.Sales_agent_name = data.get('Sales_agent_name')
        credit_to_edit.Due_date = data.get('Due_date')
        credit_to_edit.Date_of_dispatch = data.get('Date_of_dispatch')
        credit_to_edit.Produce_name = data.get('Produce_name')
        credit_to_edit.Produce_type = data.get('Produce_type')
        credit_to_edit.Branch = Branch.objects.get(branch_name=data.get('Branch'))
        credit_to_edit.Tonnage = data.get('Tonnage')
        
        credit_to_edit.save()
        return redirect('deferredpayment')
    
    context = {
        'edit_credit': credit_to_edit
    }
    return render(request, 'homeapp/editcredit.html', context)

@login_required
def deletecredit(request, pk):
    credit_to_delete = Deferred_Payment.objects.get(pk=pk)
    if request.method == 'POST':
        credit_to_delete.delete()
        return redirect('deferredpayment')
    
    context = {
        'credit_to_delete': credit_to_delete
    }
    return render(request, 'homeapp/deletecredit.html', context)

@login_required
def createstock(request):
    if request.method == 'POST':
        form = AddStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('allstock')
    else:
        form = AddStockForm()
    
    return render(request, 'homeapp/createstock.html', {'form': form})

@login_required
def salesagent(request):
    if not request.user.is_salesagent:
        return HttpResponseForbidden("You do not have permission to access this page.")
    # Get total deferred payments amount
    deferred_payments = Deferred_Payment.objects.all()
    total_deferred = deferred_payments.aggregate(total=Sum('Amount_due'))['total'] or 0
    
    # Get total sales amount
    all_sales = Sale.objects.all()
    total_sales = all_sales.aggregate(total=Sum('Amount_paid'))['total'] or 0
    
    # Get recent sales limited to 10
    recent_sales = Sale.objects.all().order_by('-Date_time')[:10]
    
    context = {
        'deferred_payments': deferred_payments,
        'total_deferred': total_deferred,
        'total_sales': total_sales,
        'sales': recent_sales,  # for the recent sales table
    }
    
    return render(request, 'homeapp/dashboard2.html', context)

@login_required
def director(request):
    if not request.user.is_director:
        return HttpResponseForbidden("You do not have permission to access this page.")
    # Calculate branch-wise deferred payments
    branches = Branch.objects.all()
    branch_deferred = {}
    branch_sales = {}
    
    for branch in branches:
        # Calculate deferred payments for each branch
        deferred_total = Deferred_Payment.objects.filter(
            Branch=branch
        ).aggregate(total=Sum('Amount_due'))['total'] or 0
        branch_deferred[branch.branch_name] = deferred_total
        
        # Calculate total sales for each branch by joining through Stock
        sales_total = Sale.objects.filter(
            Name_of_produce__Branch=branch
        ).aggregate(total=Sum('Amount_paid'))['total'] or 0
        branch_sales[branch.branch_name] = sales_total
    
    # Get recent sales for all branches
    recent_sales = Sale.objects.all().order_by('-Date_time')[:10]
    
    # Get all stock items grouped by product name
    all_stocks = Stock.objects.all()
    grouped_stocks = {}
    for stock in all_stocks:
        if stock.Name_of_produce not in grouped_stocks:
            grouped_stocks[stock.Name_of_produce] = {
                'name': stock.Name_of_produce,
                'branches': {},
                'total_quantity': 0
            }
        
        branch_name = stock.Branch.branch_name if stock.Branch else 'Unassigned'
        if branch_name not in grouped_stocks[stock.Name_of_produce]['branches']:
            grouped_stocks[stock.Name_of_produce]['branches'][branch_name] = 0
        grouped_stocks[stock.Name_of_produce]['branches'][branch_name] += stock.Tonnage_in_kgs
        grouped_stocks[stock.Name_of_produce]['total_quantity'] += stock.Tonnage_in_kgs
    
    combined_stocks = list(grouped_stocks.values())
    
    context = {
        'branch_deferred': branch_deferred,
        'branch_sales': branch_sales,
        'recent_sales': recent_sales,
        'combined_stocks': combined_stocks,
    }
    
    return render(request, 'homeapp/dashboard3.html', context)

def logout_view(request):
    logout(request)
    return render(request, 'homeapp/logout.html')






