# CDP Demo API

A comprehensive Collateralized Debt Position (CDP) management API built with FastAPI, featuring liquidation simulation, risk assessment, and advanced monitoring capabilities.

## ?? Features

- **Position Management**: Create, list, and manage CDP positions
- **Liquidation System**: Simulate and execute liquidations with risk assessment
- **Price Oracle**: Real-time token price feeds with volatility simulation
- **Batch Operations**: Efficient bulk operations for multiple positions
- **Rate Limiting**: Built-in protection against API abuse
- **Comprehensive Monitoring**: Detailed metrics and health checks
- **Production Ready**: Docker support with nginx reverse proxy
- **Full Documentation**: Interactive API docs with examples

## ??? Architecture

```
???????????????????    ???????????????????    ???????????????????
?   FastAPI App   ?    ?   PostgreSQL    ?    ?  Price Oracle   ?
?                 ??????   Database      ?    ?   (Simulated)   ?
?  - REST API     ?    ?                 ?    ?                 ?
?  - Rate Limiting?    ?  - Positions    ?    ?  - ETH, BTC,    ?
?  - Validation   ?    ?  - Risk Data    ?    ?    USDC, etc.   ?
???????????????????    ???????????????????    ???????????????????
         ?
         ?
???????????????????
?   Monitoring    ?
?                 ?
?  - Metrics      ?
?  - Health Checks?
?  - Logging      ?
???????????????????
```

## ?? Prerequisites

- Python 3.13+
- PostgreSQL 16+ (for production)
- Docker & Docker Compose (optional)

## ??? Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skill-demo-backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp config.example.env .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Deployment

1. **Development environment**
   ```bash
   docker-compose up --build
   ```

2. **Production environment**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build
   ```

## ?? API Documentation

Once the application is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## ?? API Endpoints

### Core Endpoints

#### Positions
- `GET /positions/` - List all positions (paginated)
- `POST /positions/` - Create a new position

#### Liquidation
- `GET /liquidation/simulate/{position_id}` - Simulate liquidation
- `POST /liquidation/execute` - Execute liquidation

#### Metrics & Monitoring
- `GET /metrics/system` - System-wide metrics
- `GET /metrics/positions` - Position risk analysis
- `GET /metrics/health` - Detailed health checks

#### Batch Operations
- `POST /batch/positions` - Create multiple positions
- `POST /batch/simulate` - Simulate multiple liquidations
- `POST /batch/liquidate` - Execute multiple liquidations

### Health Checks
- `GET /health` - Basic health check

## ?? Usage Examples

### Creating a Position

```bash
curl -X POST "http://localhost:8000/positions/" \
  -H "Content-Type: application/json" \
  -d '{
    "position_id": "pos_001",
    "owner_address": "0x1234567890123456789012345678901234567890",
    "collateral_symbol": "ETH",
    "collateral_amount": "10.5",
    "debt_symbol": "USDC",
    "debt_amount": "25000.0"
  }'
```

### Simulating Liquidation

```bash
curl -X GET "http://localhost:8000/liquidation/simulate/pos_001"
```

### Batch Operations

```bash
curl -X POST "http://localhost:8000/batch/positions" \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {
        "position_id": "pos_001",
        "owner_address": "0x1234...",
        "collateral_symbol": "ETH",
        "collateral_amount": "10.5",
        "debt_symbol": "USDC",
        "debt_amount": "25000.0"
      },
      {
        "position_id": "pos_002",
        "owner_address": "0x5678...",
        "collateral_symbol": "WBTC",
        "collateral_amount": "1.0",
        "debt_symbol": "USDC",
        "debt_amount": "65000.0"
      }
    ]
  }'
```

## ?? Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **Rate Limiting**: 60 requests/minute, 1000 requests/hour per client
- **Error Handling**: Detailed error messages without sensitive data exposure
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## ?? Monitoring & Observability

### Metrics Available

- **System Metrics**: Total positions, liquidatable count, average health factor
- **Position Metrics**: Health distribution, risk analysis, top risky positions
- **Health Metrics**: Database status, price oracle status, resource usage

### Logging

- **Structured Logging**: JSON format with request IDs
- **Log Levels**: Configurable (DEBUG, INFO, WARNING, ERROR)
- **Request Tracking**: Full request/response logging

## ?? Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health_endpoint.py -v
```

## ?? Production Deployment

### Environment Variables

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=cdp_demo

# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=prod
LOG_LEVEL=INFO
LOG_FORMAT=json

# EVM
EVM_RPC_URL=http://localhost:8545
LIQUIDATION_EXECUTOR_ADDRESS=0x0000000000000000000000000000000000000000
```

### Docker Production

```bash
# Build and run production stack
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale API instances
docker-compose -f docker-compose.prod.yml up --scale api=3
```

## ?? Configuration

### Rate Limiting

Configure rate limits in `app/core/rate_limiting.py`:

```python
rate_limiter = RateLimiter(
    requests_per_minute=60,    # Requests per minute
    requests_per_hour=1000     # Requests per hour
)
```

### Price Oracle

The price oracle supports multiple tokens with simulated volatility:

- ETH, WBTC, USDC, USDT, DAI, LINK, UNI, AAVE
- 2% price volatility simulation
- External API fallback (simulated)

## ?? Performance

- **Async/Await**: Full async support for high concurrency
- **Database Pooling**: Efficient connection management
- **Batch Operations**: Optimized bulk operations
- **Rate Limiting**: Prevents system overload

## ?? Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## ?? License

This project is licensed under the MIT License - see the LICENSE file for details.

## ?? Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details

## ?? Future Enhancements

- [ ] Redis caching for price data
- [ ] Webhook notifications for liquidation events
- [ ] Admin panel for position management
- [ ] Enhanced health checks with detailed system status
- [ ] JWT authentication
- [ ] Database sharding for scale
- [ ] Real-time WebSocket updates
- [ ] Advanced risk models
- [ ] Integration with real blockchain networks

---

**Built with ?? using FastAPI, SQLAlchemy, and modern Python practices.**