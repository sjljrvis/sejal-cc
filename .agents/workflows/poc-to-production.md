---
description: How to graduate from POC data (CSV/JSON/PDF) to production data sources (SAP, ServiceNow, Workday, etc.)
---

# POC to Production Data Source Workflow

Use this workflow when transitioning from POC data (file uploads, flat files) to a production data source (API integration).

## Prerequisites
- Ingestion layer is set up (`app/services/ingestion/`) with at least one POC adapter
- AI Policies are defined and working with POC data
- You have access credentials for the production data source

## Steps

### 1. Audit Current Data Flows
List all data flows in the system:
- What data comes in? (entities, fields, volumes)
- Which ingestion adapter handles it currently? (CSVAdapter, JSONAdapter, etc.)
- What field mapping is used?
- Which AI Policies evaluate this data?

Document findings in a table:
```
| Entity    | Current Adapter | Fields Used        | Policies Affected    |
|-----------|----------------|--------------------|---------------------|
| Invoice   | CSVAdapter     | amount, vendor, ... | Auto-approve, Flag  |
| Ticket    | JSONAdapter    | priority, desc, ... | Route, Escalate     |
```

### 2. Identify Production Source
Document the target production data source:
- **System name:** SAP, ServiceNow, Workday, Salesforce, etc.
- **Connection type:** REST API, SOAP, SFTP, Webhook, Database
- **Authentication:** OAuth2, API Key, Certificate, Basic Auth
- **Data format:** JSON, XML, CSV extract, etc.
- **Frequency:** Real-time (webhook/streaming), Polling (every N minutes), Batch (daily/weekly)

### 3. Create Field Mapping
Create `app/services/ingestion/mappings/{source}_mapping.json`:
```json
{
    "source": "sap",
    "entity": "invoice",
    "field_map": {
        "NETWR": "amount",
        "LIFNR": "vendor_id",
        "BUKRS": "company_code",
        "BUDAT": "posting_date",
        "BELNR": "document_number"
    },
    "transformations": {
        "amount": "float",
        "posting_date": "date:YYYY-MM-DD"
    }
}
```
Compare against the POC field mapping to ensure all fields are covered.

### 4. Create Production Adapter
Create `app/services/ingestion/adapters/{source}_adapter.py`:
- Implement the `IngestionAdapter` protocol
- Use the field mapping from step 3
- Handle authentication and connection management
- Implement retry logic for transient failures
- Log all ingestion activity for monitoring

```python
class SAPAdapter(BaseAdapter):
    adapter_name = "sap"
    
    async def parse(self, raw_data: Any) -> list[dict]:
        # Transform SAP response to internal format using field mapping
        ...
    
    async def validate(self, records: list[dict]) -> tuple[list[dict], list[dict]]:
        # Validate against internal schema
        ...
    
    async def ingest(self, records: list[dict]) -> IngestionResult:
        # Push through internal service layer
        ...
    
    def health_check(self) -> HealthStatus:
        # Check API connectivity, auth status
        ...
```

### 5. Add Production Credentials
Add to `.env`:
```bash
DATA_SOURCE=sap
SAP_BASE_URL=https://sap-instance.example.com
SAP_CLIENT_ID=...
SAP_CLIENT_SECRET=...
SAP_TENANT=...
```
Update `.env.example` with placeholder values (no real secrets).

### 6. Configure Adapter Selection
Ensure `app/services/ingestion/__init__.py` supports config-driven selection:
```python
def get_adapter() -> IngestionAdapter:
    source = os.getenv("DATA_SOURCE", "csv")
    adapters = {
        "csv": CSVAdapter,
        "json": JSONAdapter,
        "sap": SAPAdapter,
        # Add production adapters here
    }
    return adapters[source]()
```

### 7. Test with Production Data Subset
- Get a small sample of production data (10-50 records)
- Run through the new adapter
- Verify records are created correctly in the database
- Compare field values against source system

### 8. Run Policy Regression
This is the critical step — verify AI Policies produce the same outcomes:
- Take the sample production data
- Run ALL active policies against it
- Compare results with the same policies run against POC data
- If outcomes differ:
  - Check if field mapping is incorrect
  - Check if data ranges/formats differ
  - Update policies if the production data reveals new patterns
- Document any policy adjustments needed

### 9. Switch Data Source
Once regression passes:
```bash
# In .env
DATA_SOURCE=sap  # Was: DATA_SOURCE=csv
```
Restart the application. The rest of the system is unaffected.

### 10. Set Up Monitoring
- Add health check endpoint that reports adapter status
- Set up alerts for:
  - Connection failures
  - High quarantine rates (> 5% of records failing validation)
  - Ingestion latency exceeding thresholds
  - Authentication token expiration warnings

### 11. Archive POC Adapters
- Do NOT delete POC adapters — keep them for testing and development
- Mark them clearly as POC: `# POC ADAPTER: Used for demo/testing with flat files`
- They remain useful for:
  - Running tests with known test data
  - Onboarding new developers
  - Demos and showcases

### 12. Update Memory Bank
- Update `docs/memory-bank/activeContext.md` with the new data source
- Update `docs/memory-bank/progress.md`
- Log the migration decision in `docs/memory-bank/decisionLog.md`:
  - Source system chosen and why
  - Field mapping decisions
  - Policy changes needed
  - Regression results
