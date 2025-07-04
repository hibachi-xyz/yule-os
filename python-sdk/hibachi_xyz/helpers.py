import asyncio
from typing import Dict, List, Optional, Union

from websockets import ClientConnection, HeadersLike
import websockets
from hibachi_xyz.types import ExchangeInfo, FutureContract, MaintenanceWindow
from datetime import datetime
from prettyprinter import cpprint
from dataclasses import asdict, dataclass

default_api_url = "https://api.hibachi.xyz"
default_data_api_url = "https://data-api.hibachi.xyz"

async def connect_with_retry(web_url: str, headers: Optional[HeadersLike] = None) -> ClientConnection:
    """Establish WebSocket connection with retry logic"""
    max_retries = 10
    retry_count = 0
    retry_delay = 1 
    
    while retry_count < max_retries:
        try:
            websocket = await websockets.connect(web_url, 
                additional_headers=headers 
            )
            return websocket
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed to connect after {max_retries} attempts: {str(e)}")
            
            print(f"Connection attempt {retry_count} failed: {str(e)}. Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    
    # This shouldn't be reached due to the exception in the loop
    return websocket

def print_data(response):
    try:
        cpprint(asdict(response))
    except:
        cpprint(response)

def get_withdrawal_fee_for_amount(exchange_info: ExchangeInfo, amount: float) -> float:
    """
    Calculate the instant withdrawal fee for a given amount.
    
    Args:
        exchange_info: The exchange information
        amount: Withdrawal amount
        
    Returns:
        float: Fee percentage for the withdrawal
    """
    fees = exchange_info.feeConfig.instantWithdrawalFees
    # Sort fees by threshold (highest first)
    sorted_fees = sorted(fees, key=lambda x: x[0], reverse=True)
    
    for threshold, fee in sorted_fees:
        if amount >= threshold:
            return fee
    
    # Default to highest fee if amount is below all thresholds
    return sorted_fees[-1][1]

def get_next_maintenance_window(exchange_info: ExchangeInfo) -> Optional[MaintenanceWindow]:
    """
    Get the next maintenance window if any exists.
    
    Args:
        exchange_info: The exchange information
        
    Returns:
        Optional[Dict]: Details about the next maintenance window or None if none exists
    """
    windows = exchange_info.maintenanceWindow
    if not windows:
        return None
    
    now = datetime.now().timestamp()
    future_windows = [w for w in windows if w.begin > now]
    
    if not future_windows:
        return None
    
    next_window = min(future_windows, key=lambda w: w.begin)

    return next_window



def format_maintenance_window(window_info: MaintenanceWindow) -> str:
    """
    Format maintenance window information into a user-friendly string.
    
    Args:
        window_info: Maintenance window information from get_next_maintenance_window
        
    Returns:
        str: Formatted string with maintenance window details
    """
    if window_info is None:
        return "No upcoming maintenance windows scheduled."
    
    # Calculate time until maintenance starts
    now = datetime.now()
    start_time = datetime.fromtimestamp(window_info.begin)
    time_until = start_time - now
    
    duration_hours_raw = float((window_info.end - window_info.begin) / 3600.0)

    # Calculate days, hours, minutes
    days = time_until.days
    hours, remainder = divmod(time_until.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    # Format the start time
    start_str = start_time.strftime("%d %B %Y at %H:%M")
    
    # Format the duration
    if duration_hours_raw < 1:
        duration_str = f"{int(duration_hours_raw * 60)} minutes"
    else:
        duration_str = f"{int(duration_hours_raw)} hour{'s' if duration_hours_raw != 1 else ''}"
    
    # Combine all information
    return (
        f"The next maintenance window starts in {days}d{hours}h{minutes}m on {start_str} "
        f"for a duration of {duration_str}. "
        f"Reason: {window_info.note}."
    )