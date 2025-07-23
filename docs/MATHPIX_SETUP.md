# Mathpix OCR Setup Guide

## Getting Mathpix API Credentials

1. **Sign up for Mathpix**: Go to [https://mathpix.com/](https://mathpix.com/)
2. **Create an account** or log in if you already have one
3. **Navigate to the API section** in your dashboard
4. **Create a new application** to get your API credentials
5. **Copy your App ID and App Key**

## Setting Up Credentials

### Option 1: Environment Variables (Recommended)

```bash
export MATHPIX_APP_ID='your_app_id_here'
export MATHPIX_APP_KEY='your_app_key_here'
```

### Option 2: Interactive Input

The script will prompt you for credentials if environment variables are not set.

## Running the Mathpix OCR

```bash
python mathpix_ocr_extractor.py
```

## Why Mathpix?

- **Optimized for Academic Content**: Specially designed for research papers, textbooks, and mathematical content
- **High Accuracy**: Superior performance on complex layouts compared to general OCR
- **LaTeX Support**: Can output mathematical expressions in LaTeX format
- **Structured Data**: Better handling of tables, equations, and formatted text
- **API-based**: No local model downloads or setup required

## Pricing

Mathpix offers a free tier with limited requests, then paid plans for higher usage. Check their website for current pricing.
