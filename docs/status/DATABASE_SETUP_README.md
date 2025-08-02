# 🗄 BMAD Database Setup Guide

## 📋 Overview

This guide will help you set up the complete database infrastructure for the BMAD microservices system using Supabase.

## ✅ What's Already Done

- ✅ Database schema created (6 schemas, 20+ tables)
- ✅ Indexes and performance optimizations
- ✅ Default data inserted (admin user, roles, templates)
- ✅ Environment variable templates created
- ✅ Docker Compose configuration ready
- ✅ Monitoring setup (Prometheus + Grafana)

## 🔧 Step-by-Step Setup

### 1. Get Your Database Password

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `hpryaikxaomzomvecgwr`
3. Navigate to **Settings > Database**
4. Copy the password from the connection string
5. Or use the "Reset database password" option

**Direct Link:** https://supabase.com/dashboard/project/hpryaikxaomzomvecgwr/settings/database

### 2. Update Environment Variables

Run the database connection setup script:

```bash
python setup_database_connection.py
```

This script will:
- Ask for your database password
- Test the connection
- Update all microservice `.env` files automatically

### 3. Verify Database Setup

Run the verification script:

```bash
python test_database_setup.py
```

This will check:
- ✅ Supabase credentials
- ✅ Database schemas and tables
- ✅ Microservices configuration
- ✅ Environment file creation

### 4. Start the System

Use the startup script:

```bash
./start_bmad.sh
```

Or manually with Docker Compose:

```bash
docker-compose up --build -d
```

## 🏗 Database Architecture

### Schemas Created

| Schema | Purpose | Tables |
|--------|---------|--------|
| `auth_service` | Authentication & Authorization | 7 tables |
| `notification_service` | Multi-channel Notifications | 4 tables |
| `agent_service` | Agent Management | 2 tables |
| `workflow_service` | Workflow Orchestration | 3 tables |
| `context_service` | Context Management | 2 tables |
| `integration_service` | External Integrations | 2 tables |

### Key Features

- **Row Level Security (RLS)** enabled on all tables
- **Automatic timestamps** with triggers
- **Performance indexes** for optimal queries
- **JSONB fields** for flexible data storage
- **Foreign key constraints** for data integrity
- **Cleanup functions** for expired data

## 🔐 Default Credentials

### Admin User
- **Email:** innovativemarketinglisbon@gmail.com
- **Password:** admin123
- **Role:** admin

### Default Roles
- `admin` - Full system access
- `user` - Basic user access
- `manager` - Team management access

## 📊 Service Ports

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| Auth Service | 8001 | http://localhost:8001 |
| Notification Service | 8002 | http://localhost:8002 |
| Agent Service | 8003 | http://localhost:8003 |
| Workflow Service | 8004 | http://localhost:8004 |
| Context Service | 8005 | http://localhost:8005 |
| Integration Service | 8006 | http://localhost:8006 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |

## 🛠 Useful Commands

### Docker Management
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart auth-service

# Check service status
docker-compose ps
```

### Database Management
```bash
# Connect to database (replace with your password)
psql postgresql://postgres:[YOUR-PASSWORD]@db.hpryaikxaomzomvecgwr.supabase.co:5432/postgres

# List schemas
\dn

# List tables in schema
\dt auth_service.*

# View table structure
\d auth_service.users
```

### Monitoring
```bash
# Access Grafana
# URL: http://localhost:3000
# Username: admin
# Password: admin

# Access Prometheus
# URL: http://localhost:9090
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify your password is correct
   - Check if Supabase is accessible
   - Ensure your IP is whitelisted

2. **Services Won't Start**
   - Check if all `.env` files exist
   - Verify Docker is running
   - Check service logs: `docker-compose logs [service-name]`

3. **Missing Tables**
   - Re-run the database setup script in Supabase SQL Editor
   - Check for any SQL errors in the execution

### Log Locations

- **Docker logs:** `docker-compose logs [service-name]`
- **Application logs:** Inside each container at `/app/logs/`
- **Database logs:** Supabase Dashboard > Logs

## 📈 Next Steps

After successful setup:

1. **Test API endpoints** at http://localhost:8000/docs
2. **Configure monitoring** in Grafana
3. **Set up CI/CD** pipelines
4. **Configure production** environment variables
5. **Set up backups** for the database

## 🔗 Useful Links

- [Supabase Documentation](https://supabase.com/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs
3. Verify database connectivity
4. Check environment variables

---

**🎉 Congratulations! Your BMAD database is now ready for development and production use.** 