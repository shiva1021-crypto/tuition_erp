# config/urls_public.py
from django.contrib import admin
from django.urls import path
from tenants.views import TenantSignupView, TenantListView
from django.http import HttpResponse

def home_view(request):
    # A simple HTML form to test the signup
    html = """
    <html>
    <body style="font-family:sans-serif; text-align:center; padding:50px;">
        <h1>Start Your Tuition ERP</h1>
        <form id="signupForm" style="display:inline-block; text-align:left; padding:20px; border:1px solid #ccc;">
            <label>Academy Name:</label><br>
            <input type="text" id="c_name" placeholder="Galaxy Academy"><br><br>
            
            <label>Subdomain (URL):</label><br>
            <input type="text" id="sub" placeholder="galaxy"><br><br>
            
            <label>Owner Email:</label><br>
            <input type="email" id="email" placeholder="owner@galaxy.com"><br><br>
            
            <label>Password:</label><br>
            <input type="password" id="pass" placeholder="******"><br><br>
            
            <button type="button" onclick="register()">Register Now</button>
        </form>
        <div id="msg" style="margin-top:20px;"></div>

        <script>
            async function register() {
                const btn = document.querySelector('button');
                btn.disabled = true;
                btn.innerText = "Creating Database... (Wait 10s)";
                
                const data = {
                    company_name: document.getElementById('c_name').value,
                    subdomain: document.getElementById('sub').value,
                    email: document.getElementById('email').value,
                    password: document.getElementById('pass').value
                };
                
                try {
                    const res = await fetch('/api/register/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    const json = await res.json();
                    
                    if(res.ok) {
                        document.getElementById('msg').innerHTML = 
                            `<a href="${json.login_url}" style="color:green; font-weight:bold; font-size:1.2rem;">
                                ✅ Success! Click here to enter ${data.company_name}
                            </a>`;
                    } else {
                        document.getElementById('msg').innerText = "Error: " + JSON.stringify(json);
                    }
                } catch(e) {
                    alert("Error connecting to server");
                }
                btn.disabled = false;
                btn.innerText = "Register Now";
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)

# config/urls_public.py
from django.contrib import admin
from django.urls import path
from tenants.views import TenantSignupView, TenantListView # <--- Import this
from django.http import HttpResponse

# ... keep home_view ...

def super_admin_dashboard(request):
    # We will inject the HTML for the dashboard here
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>SaaS Super Admin</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f1f5f9; margin: 0; padding: 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
            th { color: #64748b; font-size: 0.85rem; text-transform: uppercase; }
            .status { padding: 5px 10px; border-radius: 15px; background: #dcfce7; color: #166534; font-size: 0.8rem; font-weight: bold; }
            .btn { background: #4f46e5; color: white; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 0.9rem; }
            .btn:hover { background: #4338ca; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2><i class="fa-solid fa-network-wired"></i> SaaS Master Console</h2>
                <div>
                    <strong>Welcome, Owner</strong>
                </div>
            </div>

            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3>Registered Tuition Centers</h3>
                    <button onclick="loadTenants()" class="btn" style="background:#0f172a;"><i class="fa-solid fa-sync"></i> Refresh</button>
                </div>
                <div id="loading">Loading data...</div>
                <table id="tenant-table" style="display:none;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Institute Name</th>
                            <th>Subdomain</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="rows"></tbody>
                </table>
            </div>
        </div>

        <script>
            // 1. Fetch the data
            async function loadTenants() {
                try {
                    // We rely on session auth for the superuser (since you are logged into /admin)
                    const res = await fetch('/api/tenants/');
                    
                    if (res.status === 403) {
                        document.getElementById('loading').innerHTML = `<p style="color:red">Access Denied. Please <a href="/admin/login/?next=/super-admin/">Log In as Superuser</a> first.</p>`;
                        return;
                    }
                    
                    const data = await res.json();
                    renderTable(data);
                } catch (e) {
                    console.error(e);
                    document.getElementById('loading').innerText = "Error loading data.";
                }
            }

            // 2. Render the table
            function renderTable(data) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('tenant-table').style.display = 'table';
                const tbody = document.getElementById('rows');
                tbody.innerHTML = '';

                data.forEach(t => {
                    // Exclude the 'public' tenant from the list to avoid confusion
                    if (t.schema_name === 'public') return;

                    const dashboardUrl = `http://${t.domain_url}:8000/dashboard.html`;
                    
                    tbody.innerHTML += `
                        <tr>
                            <td>#${t.id}</td>
                            <td><span style="font-weight:bold; color:#0f172a;">${t.name}</span></td>
                            <td>${t.schema_name}</td>
                            <td><span class="status">ACTIVE</span></td>
                            <td>
                                <a href="${dashboardUrl}" target="_blank" class="btn">
                                    Open ERP <i class="fa-solid fa-external-link-alt"></i>
                                </a>
                            </td>
                        </tr>
                    `;
                });
            }

            // Load on startup
            loadTenants();
        </script>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('super-admin/', super_admin_dashboard, name='super-admin'), # <--- New Dashboard
    
    # APIs
    path('api/register/', TenantSignupView.as_view(), name='tenant-register'),
    path('api/tenants/', TenantListView.as_view(), name='tenant-list'), # <--- New API
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/register/', TenantSignupView.as_view(), name='tenant-register'),
]