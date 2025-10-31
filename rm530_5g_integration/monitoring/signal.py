"""Signal quality monitoring."""

import re
from typing import Optional
from dataclasses import dataclass

from rm530_5g_integration.core.modem import Modem
from rm530_5g_integration.utils.exceptions import SignalQualityError
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SignalQuality:
    """Signal quality metrics."""
    rssi: Optional[int] = None  # Received Signal Strength Indicator (dBm)
    rsrp: Optional[int] = None  # Reference Signal Received Power (dBm)
    rsrq: Optional[float] = None  # Reference Signal Received Quality (dB)
    sinr: Optional[float] = None  # Signal to Interference plus Noise Ratio (dB)
    network_type: Optional[str] = None  # 4G, 5G, etc.
    
    def __str__(self) -> str:
        """String representation."""
        parts = []
        if self.network_type:
            parts.append(f"Type: {self.network_type}")
        if self.rssi is not None:
            parts.append(f"RSSI: {self.rssi} dBm")
        if self.rsrp is not None:
            parts.append(f"RSRP: {self.rsrp} dBm")
        if self.rsrq is not None:
            parts.append(f"RSRQ: {self.rsrq} dB")
        if self.sinr is not None:
            parts.append(f"SINR: {self.sinr} dB")
        return ", ".join(parts) if parts else "No signal data"


def get_signal_quality(modem: Modem) -> SignalQuality:
    """
    Get signal quality from modem.
    
    Args:
        modem: Connected Modem instance
    
    Returns:
        SignalQuality object
    """
    quality = SignalQuality()
    
    try:
        # Get network registration status and signal strength
        # AT+CSQ - Signal Quality
        response = modem.get_response("AT+CSQ", timeout=3)
        if response:
            match = re.search(r'\+CSQ:\s*(\d+),\s*(\d+)', response)
            if match:
                rssi = int(match.group(1))
                # Convert to dBm (0-31 scale, where 31 = -51 dBm or better)
                if rssi == 99:
                    quality.rssi = None  # Unknown
                else:
                    quality.rssi = -113 + (rssi * 2)
                logger.debug(f"RSSI: {quality.rssi} dBm")
        
        # AT+QNWINFO - Network Information
        response = modem.get_response("AT+QNWINFO", timeout=3)
        if response:
            match = re.search(r'\+QNWINFO:\s*"([^"]+)"', response)
            if match:
                quality.network_type = match.group(1)
                logger.debug(f"Network type: {quality.network_type}")
        
        # AT+QENG="servingcell" - Serving cell information (5G/4G)
        response = modem.get_response('AT+QENG="servingcell"', timeout=3)
        if response:
            # Parse RSRP, RSRQ, SINR
            rsrp_match = re.search(r'rsrp[:\s]+(-?\d+)', response, re.IGNORECASE)
            rsrq_match = re.search(r'rsrq[:\s]+(-?\d+(?:\.\d+)?)', response, re.IGNORECASE)
            sinr_match = re.search(r'sinr[:\s]+(-?\d+(?:\.\d+)?)', response, re.IGNORECASE)
            
            if rsrp_match:
                quality.rsrp = int(rsrp_match.group(1))
                logger.debug(f"RSRP: {quality.rsrp} dBm")
            if rsrq_match:
                quality.rsrq = float(rsrq_match.group(1))
                logger.debug(f"RSRQ: {quality.rsrq} dB")
            if sinr_match:
                quality.sinr = float(sinr_match.group(1))
                logger.debug(f"SINR: {quality.sinr} dB")
        
    except Exception as e:
        logger.warning(f"Error reading signal quality: {e}")
        # Don't raise, return partial data
    
    return quality

