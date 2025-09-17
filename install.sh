#!/bin/bash

# FaceDancer and GreatFET Installation Script
# This script sets up a virtual environment and installs the necessary packages

set -e  # Exit on any error

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing FaceDancer in development mode..."
pip install -e .

echo "Installing GreatFET..."
pip install greatfet

echo "Installation complete!"
echo ""
echo "To use FaceDancer with your GreatFET device:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Connect your GreatFET device"
echo "3. Run FaceDancer scripts, e.g.:"
echo "   python legacy-applets/facedancer-host-enumeration.py"
echo ""
echo "Note: You may need to add udev rules for USB device access."