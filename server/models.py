# server/models.py
from pydantic import BaseModel, Field, AliasChoices
from typing import List, Optional, Tuple

# --- Models for Miniprogram Exported Configuration (e.g., map_beacon_config.json) ---

class MapEntity(BaseModel):
    type: str
    points: List[List[float]]
    closed: Optional[bool] = None
    color: Optional[str] = None
    lineWidth: Optional[float] = None

class MiniprogramMapInfo(BaseModel): # Renamed for clarity, matches "map" key in miniprogram JSON
    width: float
    height: float
    entities: List[MapEntity]

class MiniprogramBeaconConfig(BaseModel): # Renamed for clarity
    macAddress: str = Field(validation_alias=AliasChoices('macAddress', 'deviceId'), description="BLE MAC address")
    major: Optional[int] = None
    minor: Optional[int] = None
    name: Optional[str] = Field(default=None, validation_alias=AliasChoices('name', 'displayName'))
    txPower: int = Field(..., description="RSSI at 1m")
    x: float = Field(..., description="x coordinate in meters")
    y: float = Field(..., description="y coordinate in meters")

class MiniprogramSettings(BaseModel): # Renamed for clarity
    signalPropagationFactor: float = Field(default=2.5, description="Path loss exponent 'n'")

class MiniprogramConfig(BaseModel):
    map: MiniprogramMapInfo # Expects a top-level "map" key from miniprogram JSON
    beacons: List[MiniprogramBeaconConfig]
    settings: MiniprogramSettings


# --- Models for Web UI Configuration (e.g., web_ui_config.json) ---

class WebUIMapEntity(BaseModel):
    type: str # e.g., 'polyline'
    points: List[List[float]] # List of [x, y] coordinates
    closed: Optional[bool] = None
    # Visual properties, ensure they match what MapEditorTab.vue uses/expects
    strokeColor: Optional[str] = None 
    lineWidth: Optional[float] = None
    fillColor: Optional[str] = None # If supporting filled shapes
    # 'color' was in MiniprogramMapEntity, MapEditorTab uses strokeColor, fillColor

class WebUIMapInfo(BaseModel):
    name: Optional[str] = None # Optional name for the map layout itself
    width: float # in meters
    height: float # in meters
    entities: List[WebUIMapEntity] = []

class WebUIBeaconConfig(BaseModel):
    uuid: str = Field(..., description="iBeacon UUID")
    major: int = Field(..., description="iBeacon Major value")
    minor: int = Field(..., description="iBeacon Minor value")
    x: float = Field(..., description="x coordinate in meters")
    y: float = Field(..., description="y coordinate in meters")
    txPower: int = Field(..., description="Measured RSSI at 1m for distance calculation")
    displayName: Optional[str] = Field(default=None, description="User-friendly display name for the beacon")
    macAddress: Optional[str] = Field(default=None, description="Physical MAC address, if known/relevant")
    # deviceId is not used here as uuid/major/minor are primary keys

class WebUISettings(BaseModel):
    signalPropagationFactor: float = Field(default=2.5, ge=1.0, le=6.0, description="Path loss exponent 'n' for RSSI to distance conversion")

class WebUIConfig(BaseModel):
    map: Optional[WebUIMapInfo] = None # Map can be optional initially
    beacons: List[WebUIBeaconConfig] = []
    settings: WebUISettings


# --- Models for Server-Side Runtime Configuration (e.g., server_runtime_config.json) ---

class MqttServerConfig(BaseModel): # Renamed from MqttConfig to avoid clash if old one is kept temporarily
    brokerHost: str
    brokerPort: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    applicationID: str # e.g., your OrgID
    topicPattern: str  # e.g., "/device_sensor_data/{ApplicationID}/+/+/+/+"
    clientID: Optional[str] = Field(default=None, validation_alias=AliasChoices('clientID', 'clientId'))
    enabled: bool = Field(default=True, description="Enable or disable MQTT client")
    live_mqtt_status: Optional[str] = Field(default=None, description="Live MQTT connection status, not saved to file")

class WebServerConfig(BaseModel): # Renamed from ServerConfig
    port: int = Field(default=8000, description="Port for the FastAPI web server")

class KalmanParams(BaseModel):
    processVariance: float = Field(default=1.0, description="Kalman filter process variance Q")
    measurementVariance: float = Field(default=10.0, description="Kalman filter measurement variance R")

class ServerRuntimeConfig(BaseModel):
    mqtt: MqttServerConfig
    server: WebServerConfig
    kalman: KalmanParams


# --- Tracker Data Models (remain largely unchanged) ---

class DetectedBeacon(BaseModel):
    macAddress: str = Field(..., description="BLE MAC address detected")
    major: Optional[int] = None
    minor: Optional[int] = None
    rssi: int

class TrackerReport(BaseModel):
    trackerId: str # Corresponds to device devEui from MQTT topic
    timestamp: int # Unix ms timestamp from message payload
    detectedBeacons: List[DetectedBeacon]

class TrackerState(BaseModel):
    trackerId: str
    x: Optional[float] = None
    y: Optional[float] = None
    last_update_time: int # Unix ms timestamp (server time of this update)
    last_known_measurement_time: Optional[int] = None # Unix ms timestamp (from original report)
    last_detected_beacons: List[DetectedBeacon] = [] 
    position_history: List[Tuple[float, float, int]] = [] # List of (x, y, timestamp_ms)

# --- Old combined ConfigData and CommonSettings (can be removed after refactoring) ---
# class OldBeaconConfig(BaseModel):
#     macAddress: str = Field(validation_alias=AliasChoices('macAddress', 'deviceId'), description="BLE MAC address of the beacon (e.g., C3:00:00:3E:7D:EF)")
#     major: Optional[int] = None 
#     minor: Optional[int] = None 
#     name: Optional[str] = Field(default=None, validation_alias=AliasChoices('name', 'displayName'))
#     txPower: int # RSSI at 1m
#     x: float # meters
#     y: float # meters

# class OldMqttConfig(BaseModel):
#     brokerHost: str # No default, should be in config
#     brokerPort: int = 1883
#     username: Optional[str] = None
#     password: Optional[str] = None
#     applicationID: str # No default, your OrgID
#     topicPattern: str  # No default, e.g., "/device_sensor_data/{ApplicationID}/+/+/+/+"
#     clientID: Optional[str] = Field(default=None, validation_alias=AliasChoices('clientID', 'clientId'))

# class OldServerConfig(BaseModel):
#     port: int = 8000

# class OldCommonSettings(BaseModel):
#     signalPropagationFactor: float = 2.5 # Default value (n in path loss model)
#     kalmanProcessVariance: float = 1.0 # Uncertainty in motion model
#     kalmanMeasurementVariance: float = 10.0 # Uncertainty in position measurement

# class OldConfigData(BaseModel):
#     mapInfo: MiniprogramMapInfo # Changed to reflect it comes from miniprog
#     beacons: List[OldBeaconConfig]
#     settings: OldCommonSettings
#     mqtt: OldMqttConfig
#     server: OldServerConfig 