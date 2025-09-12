# CSG Digital Wholesale Data Chat - Complete Project Documentation

**Team:** Peak Route  
**Project Type:** Hackathon  
**Status:** Development Complete  

## 🎯 Project Overview

CSG Digital Wholesale Data Chat is an AI-powered, multi-layered data interaction system that enables natural language communication with data at multiple levels - from dashboard filtering to deep database analysis to intelligent report enhancement.

## 🌟 Vision Statement

Transform how business users interact with data by providing a conversational interface that seamlessly bridges the gap between natural language questions and complex data operations, eliminating the need for SQL knowledge while enabling sophisticated analytics.

## ✨ Current Features

- 📊 **Interactive Dashboard** with KPI metrics and visualizations
- 🤖 **AI-Powered Chat** with natural language to SQL conversion
- 🔍 **Dual Data Sources** - Local CSV files and Oracle database
- 📈 **Real-time Visualizations** with Plotly charts
- 🧠 **Business Dictionary** mapping for natural language queries
- 🔄 **Smart Query Routing** between local and Oracle data
- 🎨 **Professional UI** with responsive design

## 🏗️ Architecture

### Project Structure
```
📁 src/                               # Source code modules
├── ai_service.py                     # AI/LLM integration
├── database_tools.py                 # Oracle database management
├── data_loader.py                    # CSV data loading
├── schema_service.py                 # Schema & business dictionary
└── frontend.py                       # Streamlit UI module

📁 config/                            # Configuration files
├── aws_config.py                     # AWS Bedrock configuration
└── config.py                         # Oracle database configuration

📁 data/                              # Data files
├── csv/                              # CSV data files
└── metadata/                         # Schema and dictionary files

📁 tests/                             # Test files
└── test_bedrock.py                   # AWS Bedrock testing

📁 resources/                         # Static resources
└── logo.png                          # Application logo

📁 Root files:
├── data_chat_app.py                  # Application entry point
├── requirements.txt                  # Python dependencies
└── PROJECT.md                        # This documentation
```

### Technology Stack
- **Frontend:** Streamlit with Plotly visualizations
- **AI/LLM:** OpenAI GPT-4 or AWS Bedrock Claude 3.5 Sonnet
- **Local Data:** DuckDB for CSV querying
- **Database:** Oracle with oracledb driver
- **Data Processing:** Pandas, NumPy

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Access to Oracle Database (optional)
- OpenAI API key or AWS Bedrock access

### Installation & Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file with your credentials:
```bash
# For OpenAI (default)
OPENAI_API_KEY=your_openai_api_key_here

# For Oracle Database (optional)
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=your-host.example.com:1521/service_name

# For AWS Bedrock (alternative to OpenAI)
AWS_REGION=us-east-1
AWS_PROFILE=bedrock
BEDROCK_LLM_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

3. **Place your data:**
- Put CSV files in `data/csv/` directory
- Ensure `Buy Rates Analysis.csv` exists (semicolon-separated)

4. **Run the application:**
```bash
streamlit run data_chat_app.py
```

5. **Open your browser:**
Navigate to the displayed URL (typically http://localhost:8501)

## 🔄 LLM Provider Configuration

The application supports both OpenAI and AWS Bedrock as LLM providers.

### Current Default: OpenAI GPT-4

The app is configured to use OpenAI by default. You'll see:
- 🤖 **OpenAI GPT-4** indicator in the sidebar

### Switching to AWS Bedrock Claude 3.5 Sonnet

To switch providers, edit `src/ai_service.py`:

**Comment out OpenAI (lines ~32-33):**
```python
# USE_OPENAI = True
# client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
```

**Uncomment Bedrock (lines ~36-38):**
```python
USE_OPENAI = False
from config.aws_config import aws_config, bedrock_config
bedrock_client = aws_config.get_session().client('bedrock-runtime')
```

### Provider Comparison

| Feature | OpenAI GPT-4 | AWS Bedrock Claude 3.5 |
|---------|--------------|-------------------------|
| **Streaming** | ✅ Real-time | ❌ Full response |
| **Cost** | Pay per token | Pay per token |
| **Setup** | API key only | AWS credentials + profile |
| **Models** | GPT-4, GPT-3.5 | Claude 3.5 Sonnet |
| **Response Quality** | Excellent | Excellent |

### Testing Provider Switch
1. Restart the Streamlit app
2. Check the sidebar for the provider indicator
3. Test a query like "Show me the first 5 rows"
4. Verify response and SQL generation works

## 💡 Usage Examples

### Sample Queries to Try

**Local CSV Analysis:**
- "Show me the top 10 suppliers by volume"
- "What's the average rate by destination?"
- "Filter data where rate is greater than 50"

**Oracle Database Queries:**
- "Show me all bilateral agreements"
- "List suppliers with active contracts"
- "Find rates for UK destinations"

**Dashboard Interactions:**
- Ask about KPI metrics
- Request specific visualizations
- Filter and analyze data trends

## 🔧 Advanced Configuration

### Oracle Database Setup
1. Ensure Oracle client is installed or use thin mode
2. Configure connection string in DSN format
3. Set up proper network access and firewall rules
4. Test connection with the built-in connection tester

### Business Dictionary Customization
- Edit `data/metadata/business_dictionary.json`
- Add custom business term mappings
- Define display columns and join instructions
- Restart app to load new mappings

### Adding New Data Sources
1. Place CSV files in `data/csv/`
2. Update `data_loader.py` if needed
3. Modify column processing in `frontend.py`
4. Test with sample queries

## 🐛 Troubleshooting

### Common Issues

**OpenAI Connection:**
- Verify `OPENAI_API_KEY` in `.env` file
- Check API key validity and credits
- Ensure internet connectivity

**Oracle Database:**
- Test DNS resolution of hostname
- Verify port 1521 accessibility
- Check credentials and service name
- Use IP address if DNS fails

**Data Loading:**
- Ensure CSV files are in `data/csv/`
- Check file format (semicolon-separated)
- Verify column names match expected format

**Import Errors:**
- Run `pip install -r requirements.txt`
- Check Python version compatibility
- Verify all modules are in correct directories

### Testing Commands

```bash
# Test Oracle connection
python3 -c "from src.database_tools import init_database_connection; print('Connected' if init_database_connection() else 'Failed')"

# Test Bedrock connection
python3 tests/test_bedrock.py

# Verify data loading
python3 -c "from src.data_loader import load_data; df, msg, err = load_data(); print(f'Loaded: {len(df) if df is not None else 0} rows')"
```

## 📋 Development History

### Completed Features ✅
- [x] Basic Streamlit app structure
- [x] CSV data loading and visualization
- [x] OpenAI API integration
- [x] Interactive chat interface
- [x] Natural language to SQL conversion
- [x] Dashboard with KPI metrics
- [x] Oracle database integration
- [x] Business dictionary mapping
- [x] Dual provider support (OpenAI/Bedrock)
- [x] Professional UI with Plotly charts
- [x] Smart query routing
- [x] Error handling and validation
- [x] Modular code organization

### Technical Achievements
- **Multi-source Data Integration:** Seamlessly handles both local CSV and Oracle database queries
- **Intelligent Query Routing:** Automatically determines data source based on query content
- **Business Dictionary:** Maps natural language terms to database schema
- **Professional Dashboard:** KPI metrics, interactive charts, and responsive design
- **Flexible LLM Integration:** Support for multiple AI providers with easy switching

## 🎯 Future Enhancements

### Potential Improvements
- **Enhanced Visualizations:** More chart types and interactive features
- **Advanced Analytics:** Statistical analysis and trend detection
- **Export Capabilities:** PDF reports and data export options
- **User Management:** Authentication and personalized experiences
- **Real-time Data:** Live database connections and streaming updates
- **Mobile Optimization:** Responsive design for mobile devices

### Scalability Considerations
- **Caching Layer:** Redis for query result caching
- **Load Balancing:** Multiple app instances for high availability
- **Database Optimization:** Connection pooling and query optimization
- **Monitoring:** Application performance and usage analytics

---

## 📞 Support & Contact

For technical issues or questions:
1. Check this documentation first
2. Review error messages and logs
3. Test with sample queries
4. Verify environment configuration

**Last Updated:** September 2024  
**Version:** 1.0.0  
**Status:** Production Ready

*This document serves as the complete reference for the CSG Digital Wholesale Data Chat application.*