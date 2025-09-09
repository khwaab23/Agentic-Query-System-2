"""
Data loader module for the Agentic Query System.
Loads camera feeds data and validates encoder/decoder parameters.
"""
import json
import pandas as pd
import jsonschema
from typing import Dict, Any
from pathlib import Path


class DataLoader:
    """Handles loading and validation of all data sources."""
    
    def __init__(self, data_dir: str = "Data"):
        self.data_dir = Path(data_dir)
        self.feeds_df: pd.DataFrame = None
        self.encoder_params: Dict[str, Any] = None
        self.decoder_params: Dict[str, Any] = None
        
    def load_all_data(self) -> None:
        """Load all data sources into memory."""
        self.load_feeds_data()
        self.load_encoder_params()
        self.load_decoder_params()
        
    def load_feeds_data(self) -> pd.DataFrame:
        """Load camera feeds metadata from CSV."""
        feeds_path = self.data_dir / "Table_feeds_v2.csv"
        if not feeds_path.exists():
            raise FileNotFoundError(f"Feeds CSV not found: {feeds_path}")
            
        self.feeds_df = pd.read_csv(feeds_path)
        print(f"Loaded {len(self.feeds_df)} camera feeds")
        return self.feeds_df
        
    def load_encoder_params(self) -> Dict[str, Any]:
        """Load and validate encoder parameters."""
        params_path = self.data_dir / "encoder_params.json"
        schema_path = self.data_dir / "encoder_schema.json"
        
        if not params_path.exists():
            raise FileNotFoundError(f"Encoder params not found: {params_path}")
        if not schema_path.exists():
            raise FileNotFoundError(f"Encoder schema not found: {schema_path}")
            
        # Load parameters
        with open(params_path, 'r') as f:
            self.encoder_params = json.load(f)
            
        # Load schema and validate
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        try:
            jsonschema.validate(self.encoder_params, schema)
            print("Encoder parameters validated successfully")
        except jsonschema.ValidationError as e:
            raise ValueError(f"Encoder parameters validation failed: {e}")
            
        return self.encoder_params
        
    def load_decoder_params(self) -> Dict[str, Any]:
        """Load and validate decoder parameters."""
        params_path = self.data_dir / "decoder_params.json"
        schema_path = self.data_dir / "decoder_schema.json"
        
        if not params_path.exists():
            raise FileNotFoundError(f"Decoder params not found: {params_path}")
        if not schema_path.exists():
            raise FileNotFoundError(f"Decoder schema not found: {schema_path}")
            
        # Load parameters
        with open(params_path, 'r') as f:
            self.decoder_params = json.load(f)
            
        # Load schema and validate
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        try:
            jsonschema.validate(self.decoder_params, schema)
            print("Decoder parameters validated successfully")
        except jsonschema.ValidationError as e:
            raise ValueError(f"Decoder parameters validation failed: {e}")
            
        return self.decoder_params
        
    def get_feeds_dataframe(self) -> pd.DataFrame:
        """Get the loaded feeds dataframe."""
        if self.feeds_df is None:
            raise RuntimeError("Feeds data not loaded. Call load_all_data() first.")
        return self.feeds_df
        
    def get_encoder_params(self) -> Dict[str, Any]:
        """Get the loaded encoder parameters."""
        if self.encoder_params is None:
            raise RuntimeError("Encoder params not loaded. Call load_all_data() first.")
        return self.encoder_params
        
    def get_decoder_params(self) -> Dict[str, Any]:
        """Get the loaded decoder parameters."""
        if self.decoder_params is None:
            raise RuntimeError("Decoder params not loaded. Call load_all_data() first.")
        return self.decoder_params


# Global instance to be used by the application
data_loader = DataLoader()
