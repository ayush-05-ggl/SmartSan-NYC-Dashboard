# Dataset Guide for NYC Department of Sanitation Dashboard

## 🎯 Priority Datasets (Must-Have)

### 1. **NYC Open Data - Sanitation Collection Schedules**
- **Source**: [NYC Open Data Portal](https://opendata.cityofnewyork.gov/)
- **Search for**: "DSNY Collection Schedule" or "Sanitation Collection"
- **What to look for**:
  - Collection zones/districts
  - Pickup schedules by day
  - Borough and district boundaries
- **Why it matters**: Validates our zone structure and collection schedules
- **API Endpoint**: Can enhance `/api/zones` with real schedule data

### 2. **NYC 311 Service Requests - Sanitation Related**
- **Source**: [NYC Open Data - 311 Service Requests](https://data.cityofnewyork.gov/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)
- **What to look for**:
  - Complaint type: "Sanitation" or "DSNY"
  - Request types: Missed collection, illegal dumping, overflow, etc.
  - Location data (lat/lng)
  - Status and resolution times
- **Why it matters**: Real service request data for `/api/requests` endpoints
- **Format**: CSV or JSON API
- **Filter**: Look for recent data (last 6-12 months)

### 3. **NYC Sanitation Tonnage Data**
- **Source**: NYC Open Data or DSNY Annual Reports
- **Search for**: "DSNY Tonnage" or "Waste Collection Tonnage"
- **What to look for**:
  - Daily/weekly/monthly tonnage by district
  - Waste type breakdown (residential, commercial, recycling, organic)
  - Historical trends
- **Why it matters**: Real collection data for `/api/collections` and metrics
- **API Endpoint**: Powers `/api/collections/summary` and `/api/metrics/dashboard`

### 4. **NYC Sanitation Districts/Zones Boundaries**
- **Source**: NYC Open Data - Geographic Data
- **Search for**: "DSNY Districts" or "Sanitation Districts Shapefile"
- **What to look for**:
  - GeoJSON or Shapefile format
  - District boundaries with coordinates
  - Zone IDs matching our schema
- **Why it matters**: Map visualization and zone-specific queries
- **Format**: GeoJSON preferred (easier to work with)

## 🔥 High-Value Datasets (Nice-to-Have)

### 5. **NYC Population by District/Zone**
- **Source**: US Census or NYC Planning Department
- **What to look for**: Population counts by sanitation district
- **Why it matters**: Calculate per-capita metrics (tonnage per capita)
- **Enhances**: `/api/zones/{zone_id}/stats` endpoint

### 6. **NYC Sanitation Vehicle Fleet Data**
- **Source**: NYC Open Data or FOIL requests
- **What to look for**:
  - Vehicle types and capacities
  - Vehicle assignments by district
  - Maintenance schedules (if available)
- **Why it matters**: Real vehicle data for `/api/vehicles`
- **Note**: May be limited, but any data helps

### 7. **NYC Air Quality Data (Correlation)**
- **Source**: [NYC Open Data - Air Quality](https://data.cityofnewyork.gov/Environment/Air-Quality/c3uy-2p5r)
- **What to look for**: Air quality readings by location
- **Why it matters**: Shows correlation between waste management and environmental impact
- **Enhances**: Dashboard can show environmental benefits

### 8. **NYC Traffic/Street Data**
- **Source**: NYC Open Data - Transportation
- **What to look for**: Street network, traffic patterns
- **Why it matters**: Route optimization context
- **Enhances**: Collection route efficiency metrics

## 📊 Data Format Preferences

### Best Formats (in order):
1. **JSON/GeoJSON** - Easiest to integrate
2. **CSV** - Can convert to JSON easily
3. **API Endpoints** - Real-time data (best for demo!)
4. **Shapefiles** - Need conversion tools

### What to Avoid:
- PDFs (hard to extract)
- Excel files with complex formatting
- Proprietary formats

## 🔍 Where to Search

### Primary Sources:
1. **[NYC Open Data Portal](https://opendata.cityofnewyork.gov/)**
   - Search: "DSNY", "Sanitation", "Waste", "Collection"
   - Filter by: Recent updates, CSV/JSON format

2. **[NYC 311 Data](https://data.cityofnewyork.gov/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)**
   - Filter by: Agency = "DSNY" or "Department of Sanitation"
   - Export recent data (last 3-6 months)

3. **[NYC Planning Department](https://www.nyc.gov/site/planning/index.page)**
   - Population and demographic data
   - Geographic boundaries

4. **[DSNY Official Website](https://www.nyc.gov/site/dsny/index.page)**
   - Annual reports (may have aggregated data)
   - Collection schedules

### Secondary Sources:
- **Kaggle** - Search "NYC Sanitation" or "NYC Waste"
- **GitHub** - Look for NYC data repositories
- **Data.gov** - Federal datasets that might include NYC

## 📋 Data Requirements Checklist

For each dataset, teammates should document:

- [ ] **Source URL** - Where did you find it?
- [ ] **Data format** - CSV, JSON, API, etc.?
- [ ] **Update frequency** - Daily, weekly, monthly?
- [ ] **Date range** - How recent is the data?
- [ ] **Size** - How many records?
- [ ] **Key fields** - What columns/fields does it have?
- [ ] **Geographic coverage** - All NYC or specific boroughs?
- [ ] **License/Usage** - Can we use it for hackathon?

## 🎯 Specific Search Terms

Tell your teammates to search for these exact terms:

1. **"DSNY collection schedule"**
2. **"NYC sanitation districts"**
3. **"NYC 311 DSNY"**
4. **"NYC waste tonnage data"**
5. **"NYC sanitation zones"**
6. **"NYC recycling data"**
7. **"NYC organic waste collection"**
8. **"NYC sanitation service requests"**

## 💡 Pro Tips

1. **Start with NYC Open Data** - Most reliable source
2. **Look for APIs** - Real-time data is impressive in demos
3. **Recent data > Historical** - Last 6 months is better than 10 years
4. **Smaller, cleaner datasets** - Better than huge messy ones
5. **GeoJSON preferred** - For map visualizations
6. **Check data quality** - Missing values, duplicates, etc.

## 🔄 Integration Plan

Once datasets are found:

1. **Review data structure** - Does it match our schema?
2. **Create import script** - Convert to our MongoDB format
3. **Enhance seed_data.py** - Use real data instead of generated
4. **Update API responses** - Real data = more credible demo
5. **Document data sources** - Important for presentation

## 🚨 Red Flags to Avoid

- ❌ Datasets older than 2 years (unless historical analysis)
- ❌ Incomplete data (lots of nulls)
- ❌ Wrong geographic area (not NYC)
- ❌ Proprietary/paid datasets
- ❌ Data that requires complex cleaning (time-consuming)

## ✅ Ideal Dataset Characteristics

- ✅ Recent (last 6-12 months)
- ✅ Complete (minimal missing data)
- ✅ NYC-specific
- ✅ Free and open
- ✅ Machine-readable (JSON/CSV)
- ✅ Includes location data (lat/lng or addresses)
- ✅ Updates regularly (if API)

## 📞 What to Share with Backend Team

When teammates find datasets, they should share:

1. **Direct download link** or API endpoint
2. **Sample of the data** (first 5-10 rows)
3. **Data dictionary** (what each field means)
4. **Size** (number of records)
5. **Date range** covered
6. **Any data quality issues** they noticed

This will help us quickly integrate it into the backend!

---

**Remember**: Quality over quantity. A few good, clean datasets are better than many messy ones. Focus on data that directly supports the NYC Sanitation Department persona!

