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
from django.core.paginator import Paginator


# Create your views here.
# view for welcoming page-------------------
def index(request):
    return render(request, 'homeapp/index.html')

# view for allstock page-----------------------
@login_required
def allstock(request):
    if request.user.is_manager or request.user.is_manager_2:
        # Determine which branch to filter for
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        stocks = Stock.objects.filter(Branch=branch).order_by('-id')
        context = {
            'stocks': stocks,
            'branch_name': branch_name
        }
    elif request.user.is_salesagent or request.user.is_salesagent_2:
        # Determine which branch to filter for salesagent
        branch_name = 'Maganjo' if request.user.is_salesagent else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        stocks = Stock.objects.filter(Branch=branch).order_by('-id')
        context = {
            'stocks': stocks,
            'branch_name': branch_name
        }
    else:
        stocks = Stock.objects.all().order_by('-id')
        context = {
            'stocks': stocks
        }
    return render(request, 'homeapp/allstock.html', context)

# view for stock detail Page----------------
@login_required
def stock_detail(request, stock_id):
    stock = Stock.objects.get(id=stock_id)
    return render(request, 'homeapp/stockdetail.html', {'stock': stock})

#view for selling item page--------------
@login_required
def sell_item(request, pk):
    # Get the stock item
    sell_item = get_object_or_404(Stock, id=pk)
    
    # Check if manager can access this item's branch
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        if sell_item.Branch.branch_name != branch_name:
            return HttpResponseForbidden("You do not have permission to sell items from this branch.")

    # Initialize form with POST data if POST request, otherwise empty form
    sales_form = AddSaleForm(request.POST if request.method == 'POST' else None)
    
    if request.method == 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.Name_of_produce = sell_item
            new_sale.Branch = sell_item.Branch
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
                
                return redirect('receipt')
            else:
                # If not enough stock, add an error to the form
                sales_form.add_error('Tonnage_in_kgs', 'Not enough stock available')
    
    context = {
        'sales_form': sales_form,
        'sell_item': sell_item
    }        
    return render(request, 'homeapp/sell_item.html', context)

# view for all receipts page-------------------
@login_required
def receipt(request):
    if request.user.is_manager or request.user.is_manager_2:
        # Determine which branch to filter for
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        sales = Sale.objects.filter(Branch=branch).order_by('-id')
    elif request.user.is_salesagent or request.user.is_salesagent_2:
        # Determine which branch to filter for salesagent
        branch_name = 'Maganjo' if request.user.is_salesagent else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        sales = Sale.objects.filter(Branch=branch).order_by('-id')
    else:
        sales = Sale.objects.all().order_by('-id')
    return render(request, 'homeapp/receipt.html', {'sales': sales})

#view for login page-------------------
def Login(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_director:
                return redirect('director')
            elif user.is_manager or user.is_manager_2:  # Handle both manager types
                return redirect('manager')
            elif user.is_salesagent or user.is_salesagent_2:  # Handle both salesagent types
                return redirect('salesagent')
            else:
                messages.error(request, "Invalid user role")
        else:
            messages.error(request, "Invalid username or password")
                    
    return render(request, 'homeapp/login.html')

# view for signup page------------------------
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

#view for all sales page-------------------
@login_required
def allsales(request):
    if request.user.is_manager or request.user.is_manager_2:
        # Determine which branch to filter for
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        all_transactions = Sale.objects.filter(Branch=branch).order_by('-id')
        stocks = Stock.objects.filter(Branch=branch)  # Get stocks for this branch only
    elif request.user.is_salesagent or request.user.is_salesagent_2:
        # Determine which branch to filter for salesagent
        branch_name = 'Maganjo' if request.user.is_salesagent else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        all_transactions = Sale.objects.filter(Branch=branch).order_by('-id')
        stocks = Stock.objects.filter(Branch=branch)  # Get stocks for this branch only
    else:
        all_transactions = Sale.objects.all().order_by('-id')
        stocks = Stock.objects.all()

    paginator = Paginator(all_transactions, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'stocks': stocks,
        'branch_name': branch_name if (request.user.is_manager or request.user.is_manager_2 or request.user.is_salesagent or request.user.is_salesagent_2) else None
    }
    return render(request, 'homeapp/allsales.html', context)

@login_required
def addstock(request, pk):
    if not (request.user.is_manager or request.user.is_manager_2):
        return HttpResponseForbidden("You do not have permission to access this page.")
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
    if request.user.is_manager or request.user.is_manager_2:
        # Determine which branch to filter for
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        all_deferred_payments = Deferred_Payment.objects.filter(Branch=branch).order_by('-Due_date')
        deferredpayment = Deferred_Payment.objects.filter(Branch=branch)  # Get credit for this branch only
    elif request.user.is_salesagent or request.user.is_salesagent_2:
        # Determine which branch to filter for salesagent
        branch_name = 'Maganjo' if request.user.is_salesagent else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        all_deferred_payments = Deferred_Payment.objects.filter(Branch=branch).order_by('-id')
        deferredpayment = Deferred_Payment.objects.filter(Branch=branch)  # Get credits for this branch only
    else:
        all_deferred_payments = Deferred_Payment.objects.all().order_by('-Due_date')
        deferredpayment = Deferred_Payment.objects.all()
    
    paginator = Paginator(all_deferred_payments, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'deferredpayment': deferredpayment,
        'branch_name': branch_name if (request.user.is_manager or request.user.is_manager_2) else None
    }  
    return render(request, 'homeapp/deferredpayment.html', context)

@login_required
def add_deferredpayment(request):
    if request.method == 'POST':
        form = AddDeferred_PaymentForm(request.POST)
        if form.is_valid():
            deferred_payment = form.save(commit=False)
            
            # If user is a manager, set the branch automatically
            if request.user.is_manager or request.user.is_manager_2:
                branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
                branch = Branch.objects.get(branch_name=branch_name)
                deferred_payment.Branch = branch
                
            deferred_payment.save()
            return redirect('deferredpayment')
    else:
        form = AddDeferred_PaymentForm()
    
    # Filter stocks and branches based on manager type
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        stocks = Stock.objects.filter(Branch=branch)
        branches = Branch.objects.filter(branch_name=branch_name)
    else:
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
    
    # Check if manager has access to this sale's branch
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        if tx_to_edit.Branch and tx_to_edit.Branch.branch_name != branch_name:
            return HttpResponseForbidden("You do not have permission to edit sales from this branch.")
    
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
    
    # Filter stock list based on manager type
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        branch = Branch.objects.get(branch_name=branch_name)
        stock_list = Stock.objects.filter(Branch=branch)
    else:
        stock_list = Stock.objects.all()
    
    context = {
        "edit_details": tx_to_edit,
        "stock_list": stock_list
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
        return redirect('allsales')
    
    context = {
        "details": to_delete
    }
    return render(request, 'homeapp/delete.html', context)

@login_required
def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Sale, id=receipt_id)
    
    # Check if manager has access to this receipt's branch
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        if receipt.Branch.branch_name != branch_name:
            return HttpResponseForbidden("You do not have permission to view receipts from this branch.")
            
    return render(request, 'homeapp/receipt_detail.html', {'receipt': receipt})

@login_required
def manager(request):
    if not (request.user.is_manager or request.user.is_manager_2):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    # Determine which branch to filter for
    branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
    branch = Branch.objects.get(branch_name=branch_name)

    # Get stock items for this branch only
    all_stocks = Stock.objects.filter(Branch=branch)
    
    # Create a dictionary to group stocks by product name
    grouped_stocks = {}
    for stock in all_stocks:
        if stock.Name_of_produce not in grouped_stocks:
            grouped_stocks[stock.Name_of_produce] = {
                'name': stock.Name_of_produce,
                'branches': {},
                'total_quantity': 0
            }
        
        if branch_name not in grouped_stocks[stock.Name_of_produce]['branches']:
            grouped_stocks[stock.Name_of_produce]['branches'][branch_name] = 0
        grouped_stocks[stock.Name_of_produce]['branches'][branch_name] += stock.Tonnage_in_kgs
        grouped_stocks[stock.Name_of_produce]['total_quantity'] += stock.Tonnage_in_kgs
    
    # Convert dictionary to list for template
    combined_stocks = list(grouped_stocks.values())
    
    # Get recent sales for this branch only
    recent_sales = Sale.objects.filter(Branch=branch).order_by('-Date_time')[:4]
    
    # Get low stock items for this branch only
    low_stock_items = Stock.objects.filter(Branch=branch, Tonnage_in_kgs__lt=100)
    
    context = {
        'combined_stocks': combined_stocks,
        'recent_sales': recent_sales,
        'low_stock_items': low_stock_items,
        'branch_name': branch_name,
    }
    
    return render(request, 'homeapp/dashboard1.html', context)

@login_required
def viewcredit(request, pk):
    credit = get_object_or_404(Deferred_Payment, pk=pk)
    
    # Check if manager has access to this credit's branch
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        if credit.Branch.branch_name != branch_name:
            return HttpResponseForbidden("You do not have permission to view credits from this branch.")
            
    context = {
        "creditdetails": credit
    }
    return render(request, 'homeapp/viewcredit.html', context)

@login_required
def editcredit(request, pk):
    credit_to_edit = get_object_or_404(Deferred_Payment, pk=pk)
    
    # Check if manager has access to this credit's branch
    if request.user.is_manager or request.user.is_manager_2:
        branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
        if credit_to_edit.Branch.branch_name != branch_name:
            return HttpResponseForbidden("You do not have permission to edit credits from this branch.")
    
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
    if not (request.user.is_manager or request.user.is_manager_2):
        return HttpResponseForbidden("You do not have permission to access this page.")
        
    if request.method == 'POST':
        form = AddStockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            # Set the branch based on manager type
            branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
            branch = Branch.objects.get(branch_name=branch_name)
            stock.Branch = branch
            stock.save()
            return redirect('allstock')
    else:
        form = AddStockForm()
        
    # Get the branch name for context
    branch_name = 'Maganjo' if request.user.is_manager else 'Matugga'
    return render(request, 'homeapp/createstock.html', {
        'form': form,
        'branch_name': branch_name
    })

@login_required
def salesagent(request):
    if not (request.user.is_salesagent or request.user.is_salesagent_2):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    # Determine which branch to filter for
    branch_name = 'Maganjo' if request.user.is_salesagent else 'Matugga'
    branch = Branch.objects.get(branch_name=branch_name)
    
    # Get stock items for this branch only
    stock_items = Stock.objects.filter(Branch=branch)
    
    # Get sales for this branch only
    sales = Sale.objects.filter(Branch=branch).order_by('-Date_time')[:5]
    
    # Calculate total sales amount for this branch
    total_sales = Sale.objects.filter(Branch=branch).aggregate(
        total=Sum('Amount_paid')
    )['total'] or 0
    
    # Calculate total deferred payments for this branch
    total_deferred = Deferred_Payment.objects.filter(Branch=branch).aggregate(
        total=Sum('Amount_due')
    )['total'] or 0
    
    context = {
        'stock_items': stock_items,
        'sales': sales,
        'branch_name': branch_name,
        'total_sales': total_sales,
        'total_deferred': total_deferred
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
        
        # Calculate total sales for each branch
        sales_total = Sale.objects.filter(
            Name_of_produce__in=Stock.objects.filter(Branch=branch)
        ).aggregate(total=Sum('Amount_paid'))['total'] or 0
        branch_sales[branch.branch_name] = sales_total
    
    # Get recent sales for all branches
    recent_sales = Sale.objects.all().order_by('-Date_time')[:10]
    
    # Get all stock items grouped by product name
    all_stocks = Stock.objects.all()
    
    # Group stocks by product name
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





