"""Input validation utilities."""


class SymbolValidator:
    """Validates stock symbols."""
    
    def is_valid_symbol(self, symbol: str) -> bool:
        """Validate stock symbol format."""
        if not isinstance(symbol, str):
            return False
        
        # Basic validation rules
        symbol = symbol.strip().upper()
        
        # Length check (1-5 characters for most markets)
        if not (1 <= len(symbol) <= 5):
            return False
        
        # Only letters allowed
        if not symbol.isalpha():
            return False
        
        return True