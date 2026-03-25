import os

class WarningLogger:
    """
    Manages warning logs for the sumo parser.
    
    This class is designed to be used as a singleton. A single instance `logger`
    is created at the module level. It must be configured by calling
    `logger.initialize()` once at the start of the application.
    """
    def __init__(self):
        """Initializes the logger in an unconfigured state."""
        self.output_dir = None
        self.banzuke_warnings = None
        self.format_warnings = None
        self._initialized = False

    def initialise(self, output_dir):
        """
        Configure the logger, create directories, and open log files.
        This method should only be called once.
        
        Args:
            output_dir: Base directory for warning output files
        """
        if self._initialized:
            print("Warning: Logger already initialized.")
            return

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'warnings'), exist_ok=True)
        
        # Initialize banzuke warnings file
        self.banzuke_warnings = open(os.path.join(output_dir, 'banzuke warnings.html'), 'w', encoding='UTF8')
        self.banzuke_warnings.write('Banzuke Warnings<br />\n')
        
        # Initialize file format warnings file
        self.format_warnings = open(os.path.join(output_dir, 'file-format weirdness.html'), 'w', encoding='UTF8')
        self.format_warnings.write('Old Format Files<br />\n')
        self._initialized = True

    def _check_initialized(self):
        """Ensures the logger is initialized before use."""
        if not self._initialized:
            raise RuntimeError("WarningLogger has not been initialized. Call logger.initialize() first.")

    def log_banzuke_warning(self, year, month, division_abbr, link_text=None):
        """Log a warning about banzuke data not conforming to the model."""
        self._check_initialized()
        link = f'https://sumodb.sumogames.de/Banzuke.aspx?b={year}{month:02d}#{division_abbr}'
        display_text = link_text or link
        self.banzuke_warnings.write(f'<a href="{link}">{display_text}</a><br/>\n')
    
    def log_format_warning(self, year, month, day):
        """Log a warning about unexpected file format."""
        self._check_initialized()
        self.format_warnings.write(f'!=12 format {year}{month:02d}, day {day}<br />\n')
    
    def log_validation_warnings(self, year, month, warnings):
        """Log validation warnings for a BashoState object."""
        self._check_initialized()
        if not warnings:
            return
            
        with open(f"{self.output_dir}/warnings/state {year} {month:02d}.txt", 'w', encoding='UTF8') as f:
            for warning in warnings:
                f.write(f"WARNING: {warning['message']} (model ref: {warning['model_ref']})\n")
    
    def log_chii_warnings(self, year, month, warnings):
        """Log chii warnings (west without an east)."""
        self._check_initialized()
        if not warnings:
            return
            
        with open(f"{self.output_dir}/warnings/chii {year} {month:02d}.txt", 'w', encoding='UTF8') as f:
            for ky, val in warnings.items():
                f.write(f'{ky}:\n')
                for v in val:
                    f.write(f"    {v}\n")
    
    def close(self):
        """Close all warning log files if they were opened."""
        if self.banzuke_warnings:
            self.banzuke_warnings.close()
        if self.format_warnings:
            self.format_warnings.close()
        self._initialized = False

logger = WarningLogger()
