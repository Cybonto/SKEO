# SKEO - Scientific Knowledge Extraction Ontology Tool

SKEO is a comprehensive tool designed to extract structured knowledge from scientific papers according to the Scientific Knowledge Extraction Ontology. It processes PDF documents and extracts various components such as research problems, methodologies, challenges, and opportunities in a structured format that can be imported into a Strapi-based knowledge management system.

## Overview

SKEO leverages AI language models to extract structured knowledge from scientific papers, providing researchers with valuable insights into the scientific landscape. The tool follows the Scientific Knowledge Extraction Ontology (SKEO) framework to categorize and organize this knowledge.

Key components that SKEO extracts include:

- Research Context
- Theoretical Basis
- Research Problems
- Knowledge Gaps
- Research Questions
- Scientific and Methodological Challenges
- Methodological Frameworks
- Future Directions
- Potential Applications
- Limitations

## Program Flows
```mermaid
  graph TD
      subgraph Initialization [skeo.py]
          A[Start] --> B{Parse Args};
          B --> C[Load Params];
          C -- Params --> D[Init SKEOExtractor];
      end
  
      subgraph PDF Discovery [skeo.py]
          D --> E[Scan PDF Dir Recursively];
          E --> F{Output Exists?};
          F -- Yes --> G[Skip PDF];
          F -- No --> H[Add PDF to Process List];
          G --> E;
          H --> I[All PDFs Scanned?];
          I -- No --> E;
          I -- Yes --> J{Any PDFs to Process?};
      end
  
      subgraph Extractor Init [skeo_extractor.py]
          D -- Params --> D1[Init LLMClient];
          D -- Params --> D2[Init MetadataFetcher];
          D -- Params --> D3[Init PDFProcessor];
          D -- Params --> D4[Init PromptManager];
          D -- Params --> D5{Direct Upload?};
          D5 -- Yes --> D6[Init StrapiClient];
      end
  
      subgraph Concurrent Processing Loop [skeo.py]
          direction LR
          J -- Yes --> K[Start Async Loop w/ Semaphore];
          K --> L(Process Single PDF);
          L --> M{More PDFs?};
          M -- Yes --> K;
          M -- No --> N[Gather Results];
      end
  
      subgraph Single PDF Processing [skeo_extractor.py - process_pdf]
          L --> P1[Generate Paper ID];
          P1 --> P2[Call PDFProcessor.extract_text_from_pdf];
          P2 -- Text/Metadata --> P3[Validate Paper Data];
          P3 --> P4[Async Extract Components];
          P4 -- Components --> P5[Aggregate Results & Confidence];
          P5 --> P6[Add Relationships];
          P6 -- Aggregated Data --> P7[Call Save/Upload];
          P7 --> L;
      end
  
      subgraph Text/Metadata Extraction [pdf_processor.py - extract_text_from_pdf]
          P2 --> T1[Extract Basic Metadata];
          T1 --> T2[Attempt Title Extraction];
          T2 -- Title/Author --> T3{Search Metadata?};
          T3 -- Yes --> T4[Call MetadataFetcher];
          T3 -- No --> T5;
          T4 -- Online Meta --> T5[Consolidate Metadata];
          T1 -- Basic Meta --> T5;
          T2 -- Validated Title --> T5;
          T5 -- Initial Meta --> T6{Extraction Method?};
          T6 -- Docling --> T7[Call _extract_with_docling];
          T6 -- PyMuPDF --> T8[Call _extract_with_pymupdf];
          T7 -- Extracted Text --> T9;
          T8 -- Extracted Text --> T9[Refine Metadata from Text];
          T9 -- Final Text/Meta --> P2;
      end
  
      subgraph Component Extraction [skeo_extractor.py - _extract_single_component]
          style P4 fill:#f9f,stroke:#333,stroke-width:2px
          P4 --> C1[Get Prompt from PromptManager];
          C1 -- Prompt --> C2[Call LLMClient.extract_json];
          C2 -- Raw JSON --> C3{Validate Schema?};
          C3 -- Valid --> C4[Add IDs/Links];
          C3 -- Invalid --> C2;
          C4 -- Validated Component --> P4;
      end
  
      subgraph Save & Upload [skeo_extractor.py - _save_and_upload_result]
          P7 --> S1[Prepare Data for Strapi];
          S1 --> S2[Save JSON Locally];
          S2 --> S3{Direct Upload?};
          S3 -- Yes --> S4[Call StrapiClient.upload_data];
          S3 -- No --> P7;
          S4 --> P7;
      end
  
      subgraph Strapi Upload [strapi_client.py - upload_data]
          style S4 fill:#ccf,stroke:#333,stroke-width:2px
          S4 --> U1[Order Entities by Dependency];
          U1 --> U2[Loop Through Entities];
          U2 --> U3["Resolve Relationships (Internal ID -> Strapi ID)"]; %% <-- Line fixed here
          U3 --> U4[Call _upload_single_entity];
          U4 -- Success --> U5[Store Strapi ID];
          U4 -- Failure --> U6[Log Error];
          U5 --> U2;
          U6 --> U2;
          U2 -- Done --> S4;
      end
  
      subgraph Finalization [skeo.py]
          N --> Z[Log Summary];
          J -- No --> Z;
          Z --> ZA[End];
      end
  
      %% Styling for key modules/subprocesses
      style L fill:#eee,stroke:#333,stroke-width:2px
      style P2 fill:#eee,stroke:#333,stroke-width:2px
      style C2 fill:#eee,stroke:#333,stroke-width:2px
      style T4 fill:#eee,stroke:#333,stroke-width:2px
```
    
## Installation

### Requirements

Ensure you have Python 3.8+ installed.

### Option 1: Install using uv (recommended)

[uv](https://github.com/astral-sh/uv) is a fast, reliable Python package installer and resolver.

```bash
# Install uv if you haven't already
pip install uv

# Clone the repository
git clone https://github.com/yourusername/skeo.git
cd skeo

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r skeo-requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

Note: if you have pip related issues in downloading the spaCy model, ensure pip in correctly installed and is accessible. Run the following command
```bash
python -m ensurepip --upgrade
```

### Option 2: Install using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/skeo.git
cd skeo

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r skeo-requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

### Dependencies

See the `skeo-requirements.txt` file for a complete list of dependencies. Main requirements include:

- aiohttp
- beautifulsoup4
- docling
- PyMuPDF
- langdetect
- pydantic
- python-dotenv
- PyYAML
- requests
- spacy
- tenacity

## Configuration

### Environment Variables

Copy the sample environment file and customize it with your API keys and settings:

```bash
cp sample.env .env
# Edit .env with your preferred text editor
```

Required environment variables include:

- `LLM_API_ENDPOINT`: API endpoint for the language model service
- `LLM_API_KEY`: API key for the language model service
- `LLM_MODEL_NAME`: Name of the language model to use
- `GOOGLE_SCHOLAR_API_KEY` (optional): API key for Google Scholar metadata lookup
- `GOOGLE_SCHOLAR_CX` (optional): Custom Search Engine ID for Google Scholar
- `STRAPI_URL`: URL of your Strapi instance (default: http://localhost:1337)
- `STRAPI_API_TOKEN`: API token for Strapi authentication

### Parameters

You can customize SKEO's behavior using a parameters YAML file. See the sample `skeo-params.yaml` for configuration options.

## Usage

### Basic Usage

```bash
python skeo.py --pdf-dir /path/to/pdfs --output-dir /path/to/output
```

### Command Line Options

```
usage: skeo.py [-h] --pdf-dir PDF_DIR [--prompt-file PROMPT_FILE] [--output-dir OUTPUT_DIR] [--params-file PARAMS_FILE] [--strapi-url STRAPI_URL] [--strapi-token STRAPI_TOKEN]

SKEO - Scientific Knowledge Extraction Ontology Tool

options:
  -h, --help            show this help message and exit
  --pdf-dir PDF_DIR, -d PDF_DIR
                        Directory containing PDF files to process
  --prompt-file PROMPT_FILE, -p PROMPT_FILE
                        YAML file containing extraction prompts (default: skeo_prompts.yaml)
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory to save extraction output (default: skeo_output)
  --params-file PARAMS_FILE
                        YAML file containing parameters (default: use built-in defaults)
  --strapi-url STRAPI_URL, -s STRAPI_URL
                        Strapi API URL (default: from STRAPI_URL env var or http://localhost:1337)
  --strapi-token STRAPI_TOKEN, -t STRAPI_TOKEN
                        Strapi API token (default: from STRAPI_API_TOKEN env var)

Extracts structured knowledge from scientific papers according to the SKEO ontology
```

### Output Format

For each processed PDF, SKEO creates a JSON file containing the structured extraction results in a format compatible with the Strapi content management system. The output includes all extracted SKEO components with their relationships preserved.

## Advanced Configuration

### Customizing Extraction Prompts

You can customize the prompts used for each knowledge component by editing the `skeo_prompts.yaml` file.

### Parameters Configuration

The `skeo-params.yaml` file allows you to control various aspects of SKEO's behavior:

- LLM settings (model, temperature, tokens)
- PDF processing options
- Extraction components to include/exclude
- Parallel processing settings
- Direct upload to Strapi

## Strapi Integration

SKEO can directly upload extracted knowledge to a Strapi instance with the appropriate content models. Set `direct_upload: true` in your parameters file to enable this feature.

Before uploading, SKEO will test the connection and endpoints to ensure compatibility.

## Folder Structure

```
.
├── skeo.py                 # Main script
├── skeo_prompts.yaml       # Extraction prompts
├── skeo-params.yaml        # Configuration parameters
├── skeo-requirements.txt   # Dependencies
├── sample.env              # Sample environment variables
├── README.md               # This documentation
└── skeo_output/            # Default output directory
```

## Troubleshooting

### Common Issues

1. **LLM API Connection Errors**:
   - Check that your `LLM_API_ENDPOINT` and `LLM_API_KEY` are correct
   - Verify your network connection and any proxy settings

2. **PDF Processing Errors**:
   - Ensure PDFs are properly formatted and readable
   - Try the alternative extraction method by setting `extract_method: "pymupdf"` in parameters

3. **Strapi Upload Issues**:
   - Verify your Strapi URL and API token
   - Check that your Strapi instance has the required content types
   - Run with `test_endpoints: true` to validate connectivity

### Logs

Check the `skeo_extraction.log` file for detailed logs of the extraction process.

## License

Creative Commons

## Acknowledgements

SKEO is based on the Scientific Knowledge Extraction Ontology (SKEO) research developed by Tam Nguyen. SKEO leverages existing ontologies.
