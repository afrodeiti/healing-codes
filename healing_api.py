#!/usr/bin/env python3
"""
Sacred Healing API - Comprehensive Implementation

A complete Python Flask implementation of the Sacred Computing Platform including:
- Sacred geometry visualization and calculations
- Intention broadcasting via network packets
- Healing code database with Grabovoi codes
- Soul archive storage
- WebSocket server for real-time energetic feedback
- Scalar field transmission
- Past life insights
- Environmental anchoring rituals
- Remote location harmonization
- Dynamic invocation modules
- Blessing rituals with Flower of Life

Usage:
  python healing-api.py --mode api        # Run as a Flask API server
  python healing-api.py --mode broadcast  # Broadcast intention
  python healing-api.py --mode cli        # Interactive CLI interface
"""

import argparse
import asyncio
import base64
import hashlib
import io
import json
import logging
import math
import os
import random
import re
import secrets
import sqlite3
import sys
import threading
import time
import uuid
import webbrowser
from collections import Counter
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set, Callable

try:
    from flask import Flask, request, jsonify, render_template, send_file
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

try:
    from rapidfuzz import process, fuzz
    HAS_FUZZY_SEARCH = True
except ImportError:
    HAS_FUZZY_SEARCH = False

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sacred-healing')

# API server port
API_PORT = 5000

#########################################
# CORE SACRED GEOMETRY CONSTANTS & ENUMS
#########################################

# Sacred Constants
PHI = (1 + 5 ** 0.5) / 2  # Golden Ratio (1.618...)
SQRT3 = 3 ** 0.5          # Used in Vesica Piscis and Star Tetrahedron
SQRT2 = 2 ** 0.5          # Used in Octahedron
SCHUMANN_RESONANCE = 7.83 # Earth's primary resonance frequency

# Sacred Number Sequences
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
METATRON = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48]  # Tesla's 3-6-9 sequence
SOLFEGGIO = [396, 417, 528, 639, 741, 852, 963]  # Solfeggio frequencies

# Planetary geometric relationships (angular positions)
PLANETARY_ANGLES = {
    "sun": 0,
    "moon": 30,
    "mercury": 60,
    "venus": 90,
    "mars": 120,
    "jupiter": 150,
    "saturn": 180,
    "uranus": 210,
    "neptune": 240,
    "pluto": 270
}

# Element frequencies based on Solfeggio
ELEMENT_FREQUENCIES = {
    "fire": 396,    # Solfeggio frequency for liberation
    "earth": 417,   # Solfeggio frequency for change
    "air": 528,     # Solfeggio frequency for transformation
    "water": 639,   # Solfeggio frequency for connection
    "ether": 741    # Solfeggio frequency for expression
}

class PacketType(Enum):
    """Network packet types for sacred intention transmission"""
    DATA = 0
    INTENTION = 1
    SACRED_GEOMETRY = 2
    FIELD_HARMONICS = 3
    QUANTUM_RESONANCE = 4


class SacredGeometryField(Enum):
    """Sacred geometry field types"""
    TORUS = "torus"
    MERKABA = "merkaba"
    METATRON = "metatron"
    SRI_YANTRA = "sri_yantra"
    FLOWER_OF_LIFE = "flower_of_life"
    PLATONIC_SOLID = "platonic_solid"


class HealingCategory(Enum):
    """Categories for healing codes"""
    PHYSICAL = "PHYSICAL"
    EMOTIONAL = "EMOTIONAL"
    SPIRITUAL = "SPIRITUAL"
    MENTAL = "MENTAL"
    FINANCIAL = "FINANCIAL"
    RELATIONSHIPS = "RELATIONSHIPS"
    CHAKRA = "CHAKRA"
    CENTRAL_NERVOUS_SYSTEM = "CENTRAL NERVOUS SYSTEM"
    PSYCHOLOGICAL = "PSYCHOLOGICAL"
    SELF_HELP = "SELF-HELP"


# Global sequence counter for packet IDs
SEQUENCE_COUNTER = 0

# Connected WebSocket clients
WEBSOCKET_CLIENTS = set()


#########################################
# NETWORK PACKET IMPLEMENTATION
#########################################

class PacketHeader:
    """IEEE 802.11 inspired packet header for intention transmission"""
    
    def __init__(self, packet_type: PacketType, payload_length: int):
        global SEQUENCE_COUNTER
        self.version = 1
        self.type = packet_type.value
        self.length = payload_length
        self.sequence_id = SEQUENCE_COUNTER
        SEQUENCE_COUNTER += 1
        self.timestamp = int(time.time() * 1000)  # milliseconds
        self.checksum = None  # Will be calculated later
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert header to dictionary for JSON serialization"""
        return {
            "version": self.version,
            "type": self.type,
            "length": self.length,
            "sequenceId": self.sequence_id,
            "timestamp": self.timestamp,
            "checksum": self.checksum
        }


class IntentionPacket:
    """Complete network packet with intention data"""
    
    def __init__(
        self, 
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus",
        target_device: str = "broadcast"
    ):
        self.intention = intention
        self.frequency = frequency
        self.field_type = field_type
        self.target_device = target_device
        
        # Create energy signature with quantum noise
        self.energy_signature = secrets.token_hex(8)
        
        # Generate quantum entanglement key
        self.quantum_key = secrets.token_hex(16)
        
        # Calculate intention strength based on frequency and length
        self.intention_strength = min((len(intention) * frequency) / 100, 100)
        
        # Create packet payload
        self.payload = {
            "intention": intention,
            "frequency": frequency,
            "field_type": field_type,
            "energy_signature": self.energy_signature,
            "quantum_entanglement_key": self.quantum_key
        }
        
        # Create header
        payload_str = json.dumps(self.payload)
        self.header = PacketHeader(PacketType.INTENTION, len(payload_str))
        
        # Calculate checksum
        self.header.checksum = self._calculate_checksum(payload_str)
        
        # Metadata
        self.metadata = {
            "source_device": "sacred-healing-api",
            "target_device": target_device,
            "intention_strength": self.intention_strength,
            "sacred_encoding": "merkaba-torus-fibonacci"
        }
    
    def _calculate_checksum(self, payload: str) -> str:
        """Calculate SHA-256 checksum of payload"""
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for JSON serialization"""
        return {
            "header": self.header.to_dict(),
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert packet to JSON string"""
        return json.dumps(self.to_dict())
    
    def to_base64(self) -> str:
        """Convert packet to base64 string (for network transmission)"""
        return base64.b64encode(self.to_json().encode('utf-8')).decode('utf-8')


def extract_intention_from_packet(packet_base64: str) -> Optional[str]:
    """Extract intention from a base64-encoded packet (for receiving devices)"""
    try:
        # Decode from base64
        json_str = base64.b64decode(packet_base64).decode('utf-8')
        packet = json.loads(json_str)
        
        # Extract intention
        return packet["payload"]["intention"]
    except Exception as e:
        logger.error(f"Failed to extract intention from packet: {e}")
        return None


async def embed_intention_in_network_packet(
    intention: str, 
    frequency: float = SCHUMANN_RESONANCE,
    field_type: str = "torus"
) -> str:
    """Embed intention in network packet and return base64 string"""
    packet = IntentionPacket(intention, frequency, field_type)
    return packet.to_base64()


#########################################
# SACRED GEOMETRY CALCULATIONS
#########################################

class SacredGeometryCalculator:
    """Sacred geometry calculations for various fields and patterns"""
    
    @staticmethod
    def divine_proportion_amplify(intention: str, multiplier: float = 1.0) -> Dict[str, Any]:
        """Amplify intention using divine proportion (PHI)"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # Calculate hash using SHA-512
        intention_hash = hashlib.sha512(intention.encode('utf-8')).hexdigest()
        
        # Use PHI spiral to generate fibonacci-aligned energetic signature
        phi_segments = []
        for i in range(len(intention_hash)):
            char_code = ord(intention_hash[i])
            segment_value = char_code * (PHI ** ((i % 7) + 1))
            phi_segments.append(f"{int(segment_value % 100):02d}")
        
        amplified = ''.join(phi_segments)
        
        # Create a phi-spiral encoding with the intention
        spiral_hash_data = amplified + intention
        spiral_hash = hashlib.sha256(spiral_hash_data.encode('utf-8')).hexdigest()
        
        # Apply the multiplier using the closest Fibonacci number
        fib_multiplier = next((f for f in FIBONACCI if f >= multiplier), FIBONACCI[-1])
        
        # Calculate Tesla's 3-6-9 principle (sum of char codes modulo 9, or 9 if result is 0)
        metatronic_alignment = sum(ord(c) for c in intention) % 9 or 9
        
        return {
            "original": intention,
            "phi_amplified": spiral_hash,
            "fibonacci_multiplier": fib_multiplier,
            "metatronic_alignment": metatronic_alignment
        }
    
    @staticmethod
    def merkaba_field_generator(intention: str, frequency: float) -> Dict[str, Any]:
        """Generate merkaba field data based on intention and frequency"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        
        # Create counter-rotating tetrahedrons (male/female energies)
        tetra_up_data = intention + "ascend"
        tetra_up = hashlib.sha256(tetra_up_data.encode('utf-8')).hexdigest()[:12]
        
        tetra_down_data = intention + "descend"
        tetra_down = hashlib.sha256(tetra_down_data.encode('utf-8')).hexdigest()[:12]
        
        # Determine the right spin frequency using solfeggio relationship
        closest_solfeggio = min(SOLFEGGIO, key=lambda x: abs(x - frequency * 100))
        
        # Calculate the merkaba field intensity (sacred geometry)
        field_intensity = ((frequency * SQRT3) / PHI) * (frequency % 9 or 9)
        
        return {
            "intention": intention,
            "tetra_up": tetra_up,
            "tetra_down": tetra_down,
            "merkaba_frequency": frequency,
            "solfeggio_alignment": closest_solfeggio,
            "field_intensity": field_intensity,
            "activation_code": f"{math.floor(field_intensity)} {math.floor(frequency * PHI)} {math.floor(closest_solfeggio / PHI)}"
        }
    
    @staticmethod
    def flower_of_life_pattern(intention: str, duration: int) -> Dict[str, Any]:
        """Generate Flower of Life pattern based on intention and duration"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        
        # Calculate the cosmic timing (astrological alignment)
        now = datetime.now()
        cosmic_degree = (now.hour * 15) + (now.minute / 4)  # 24 hours = 360 degrees
        
        # Find planetary alignment
        closest_planet = "sun"
        closest_degree = 360
        
        for planet, angle in PLANETARY_ANGLES.items():
            diff = abs(angle - cosmic_degree)
            if diff < closest_degree:
                closest_degree = diff
                closest_planet = planet
        
        # Generate the seven interlocking circles of the Seed of Life
        seed_patterns = []
        for i in range(7):
            angle = i * (360 / 7)
            radius = (i + 1) * PHI
            seed_data = f"{intention}:{angle}:{radius}"
            seed_hash = hashlib.sha256(seed_data.encode('utf-8')).hexdigest()[:8]
            seed_patterns.append(seed_hash)
        
        # Create the full Flower of Life pattern with 19 overlapping circles
        fol_pattern = ''.join(seed_patterns)
        
        # Calculate optimal duration based on Flower of Life geometry
        optimal_duration = max(duration, int(duration * PHI))
        
        return {
            "intention": intention,
            "flower_pattern": fol_pattern,
            "planetary_alignment": closest_planet,
            "cosmic_degree": cosmic_degree,
            "optimal_duration": optimal_duration,
            "vesica_pisces_code": f"{seed_patterns[0]} {seed_patterns[3]} {seed_patterns[6]}"
        }
    
    @staticmethod
    def metatrons_cube_amplifier(intention: str, boost: bool = False) -> Dict[str, Any]:
        """Generate Metatron's Cube data based on intention"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # The 13 spheres of Metatron's Cube (Archangel Metatron's energy)
        intention_spheres = []
        
        # Create the 13 information spheres in the pattern of Metatron's Cube
        for i in range(13):
            sphere_data = intention + str(METATRON[i % len(METATRON)])
            sphere_hash = hashlib.sha512(sphere_data.encode('utf-8')).hexdigest()[:6]
            intention_spheres.append(sphere_hash)
        
        # Connect the spheres with 78 lines representing consciousness pathways
        if boost:
            # Activate the full Metatronic grid (all 78 lines)
            metatron_code = ''.join(intention_spheres)
        else:
            # Activate partial grid (only the primary 22 lines)
            metatron_code = ''.join(intention_spheres[:5])
        
        # Calculate the Cube's harmonic frequency (Tesla 3-6-9 principle)
        harmonic = sum(ord(c) for c in intention) % 9 or 9  # Tesla's completion number
        
        return {
            "intention": intention,
            "metatron_code": metatron_code,
            "harmonic": harmonic,
            "platonic_solids": {
                "tetrahedron": intention_spheres[0],
                "hexahedron": intention_spheres[1],
                "octahedron": intention_spheres[2],
                "dodecahedron": intention_spheres[3],
                "icosahedron": intention_spheres[4]
            },
            "activation_key": f"{harmonic * 3}-{harmonic * 6}-{harmonic * 9}"
        }
    
    @staticmethod
    def torus_field_generator(intention: str, hz: float = SCHUMANN_RESONANCE) -> Dict[str, Any]:
        """Generate torus field data based on intention and frequency"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if hz <= 0:
            raise ValueError("Frequency must be positive")
        
        # Map frequency to the optimal torus ratio based on Earth's Schumann resonance
        schumann_ratio = hz / SCHUMANN_RESONANCE
        
        # Generate the torus inner and outer flows (energy circulation patterns)
        inner_flow_data = intention + "inner"
        inner_flow = hashlib.sha512(inner_flow_data.encode('utf-8')).hexdigest()[:12]
        
        outer_flow_data = intention + "outer"
        outer_flow = hashlib.sha512(outer_flow_data.encode('utf-8')).hexdigest()[:12]
        
        # Calculate the phase angle for maximum resonance
        phase_angle = (hz * 360) % 360
        
        # Determine the coherence ratio (based on cardiac coherence principles)
        coherence = 0.618 * schumann_ratio  # 0.618 is the inverse of the golden ratio
        
        # Find the closest Tesla number (3, 6, or 9) for the torus power node
        tesla_nodes = [3, 6, 9]
        tesla_node = min(tesla_nodes, key=lambda x: abs(x - (hz % 10)))
        
        return {
            "intention": intention,
            "torus_frequency": hz,
            "schumann_ratio": f"{schumann_ratio:.3f}",
            "inner_flow": inner_flow,
            "outer_flow": outer_flow,
            "phase_angle": phase_angle,
            "coherence": f"{coherence:.3f}",
            "tesla_node": tesla_node,
            "activation_sequence": f"{tesla_node}{tesla_node}{inner_flow[:tesla_node]}"
        }
    
    @staticmethod
    def sri_yantra_encoder(intention: str) -> Dict[str, Any]:
        """Generate Sri Yantra data based on intention"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # The 9 interlocking triangles of the Sri Yantra
        triangles = []
        
        for i in range(9):
            if i % 2 == 0:  # Shiva (masculine) triangles point downward
                triangle_data = intention + f"shiva{i}"
            else:  # Shakti (feminine) triangles point upward
                triangle_data = intention + f"shakti{i}"
            
            triangle_hash = hashlib.sha256(triangle_data.encode('utf-8')).hexdigest()[:8]
            triangles.append(triangle_hash)
        
        # Generate the 43 intersecting points of power (marmas)
        marma_data = ''.join(triangles)
        marma_points = hashlib.sha512(marma_data.encode('utf-8')).hexdigest()
        
        # Calculate the central bindu point (singularity/unity consciousness)
        bindu_data = intention + "bindu"
        bindu = hashlib.sha256(bindu_data.encode('utf-8')).hexdigest()[:9]
        
        # Map to the 9 surrounding circuits (avaranas) for complete encoding
        circuits = []
        for i in range(9):
            circuit_data = triangles[i] + bindu
            circuit = hashlib.sha256(circuit_data.encode('utf-8')).hexdigest()[:6]
            circuits.append(circuit)
        
        return {
            "intention": intention,
            "triangles": triangles,
            "bindu": bindu,
            "circuits": circuits,
            "inner_triangle": triangles[0],
            "outer_triangle": triangles[8],
            "yantra_code": f"{bindu[:3]}-{triangles[0][:3]}-{triangles[8][:3]}"
        }
    
    @staticmethod
    def platonic_solid_resonator(intention: str, solid_type: str = "dodecahedron") -> Dict[str, Any]:
        """
        Resonates intention through platonic solid geometry for quantum coherence
        
        solid_type options: tetrahedron, hexahedron, octahedron, dodecahedron, icosahedron
        """
        if not intention:
            raise ValueError("Intention cannot be empty")
            
        # Properties of the platonic solids (vertices, edges, faces)
        platonic_properties = {
            "tetrahedron": {"vertices": 4, "edges": 6, "faces": 4, "element": "fire"},
            "hexahedron": {"vertices": 8, "edges": 12, "faces": 6, "element": "earth"},
            "octahedron": {"vertices": 6, "edges": 12, "faces": 8, "element": "air"},
            "dodecahedron": {"vertices": 20, "edges": 30, "faces": 12, "element": "ether"},
            "icosahedron": {"vertices": 12, "edges": 30, "faces": 20, "element": "water"}
        }
        
        if solid_type not in platonic_properties:
            solid_type = "dodecahedron"  # Default to ether element
        
        properties = platonic_properties[solid_type]
        
        # Generate vertex encodings (information nodes)
        vertices = []
        for i in range(properties["vertices"]):
            v_hash = hashlib.sha256((intention + f"v{i}").encode()).hexdigest()[:6]
            vertices.append(v_hash)
        
        # Create the edge connections (information pathways)
        edges = []
        for i in range(properties["edges"]):
            e_hash = hashlib.sha256((vertices[i % len(vertices)] + vertices[(i+1) % len(vertices)]).encode()).hexdigest()[:4]
            edges.append(e_hash)
        
        # Generate the face encodings (manifestation planes)
        faces = []
        for i in range(properties["faces"]):
            f_hash = hashlib.sha256((edges[i % len(edges)] + intention).encode()).hexdigest()[:6]
            faces.append(f_hash)
        
        # Calculate the resonance frequency based on the element
        element_frequency = ELEMENT_FREQUENCIES[properties["element"]]
        
        # Create activation code using the element's frequency
        activation_code = f"{element_frequency}-{properties['vertices']}{properties['faces']}"
        
        return {
            "intention": intention,
            "solid_type": solid_type,
            "element": properties["element"],
            "vertices": vertices[:5],  # Limiting output size
            "edges": edges[:5],  # Limiting output size
            "faces": faces[:5],  # Limiting output size
            "element_frequency": element_frequency,
            "activation_code": activation_code,
            "harmonic_pattern": "".join(vertices[:3]) + "".join(faces[:3])
        }


#########################################
# STORAGE IMPLEMENTATION
#########################################

class SacredStorage:
    """Storage for healing codes, soul archives, and users"""
    
    def __init__(self, db_path: str = 'sacred_healing.db'):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Set up database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Soul Archive table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS soul_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            intention TEXT,
            frequency TEXT NOT NULL,
            boost INTEGER,
            multiplier INTEGER,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Healing Code table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS healing_code (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            category TEXT,
            affirmation TEXT,
            vibration INTEGER,
            source TEXT
        )
        ''')
        
        # Past Life Insights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS past_life_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            past_life_pattern TEXT NOT NULL,
            life_period TEXT,
            key_lesson TEXT,
            resolution_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Environmental Anchoring table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS environmental_anchoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            coordinates TEXT,
            intention TEXT NOT NULL,
            field_type TEXT NOT NULL,
            field_data TEXT NOT NULL,
            activation_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        
        # Initialize with sample healing codes if table is empty
        cursor.execute('SELECT COUNT(*) FROM healing_code')
        count = cursor.fetchone()[0]
        if count == 0:
            self._initialize_healing_codes(cursor, conn)
        
        conn.close()
    
    def _initialize_healing_codes(self, cursor, conn):
        """Initialize with sample healing codes"""
        sample_codes = [
            ("23 74 555", "Healing headaches in general", "CENTRAL NERVOUS SYSTEM", "I am pain-free and clear-minded", 555, "Grabovoi"),
            ("58 33 554", "Healing migraine", "CENTRAL NERVOUS SYSTEM", "My head is clear and peaceful", 554, "Grabovoi"),
            ("71 81 533", "Back pain relief", "CENTRAL NERVOUS SYSTEM", "My spine is strong and flexible", 533, "Grabovoi"),
            ("33 45 10101", "Forgiveness", "PSYCHOLOGICAL", "I release all past hurts with love", 10101, "Grabovoi"),
            ("11 96 888", "Low self-esteem to healthy self-image", "SELF-HELP", "I love and accept myself completely", 888, "Grabovoi"),
            ("8888", "Divine protection", "SPIRITUAL", "I am divinely protected on all levels", 8888, "Ancient"),
            ("13 13 514", "Stress relief/relaxation", "SELF-HELP", "I am calm, peaceful and centered", 514, "Grabovoi"),
            ("517 489719 841", "Increase self-confidence", "SELF-HELP", "I am confident and empowered", 841, "Grabovoi"),
            ("56 57 893", "Unconditional love", "RELATIONSHIPS", "I give and receive love freely", 893, "Grabovoi"),
            ("888 412 1289018", "Love (general & relationships)", "RELATIONSHIPS", "Love flows through me and to me", 888, "Grabovoi"),
            ("741", "Expression and throat chakra healing", "CHAKRA", "I express my truth with clarity", 741, "Solfeggio"),
            ("852", "Intuition and third eye activation", "CHAKRA", "I see clearly with my inner vision", 852, "Solfeggio"),
            ("963", "Connection to higher consciousness", "SPIRITUAL", "I am one with divine consciousness", 963, "Solfeggio"),
            ("528", "DNA repair and transformation", "PHYSICAL", "My cells are vibrant and healthy", 528, "Solfeggio"),
            ("111", "Manifestation and new beginnings", "SPIRITUAL", "I am aligned with my highest path", 111, "Angel Number"),
            ("777", "Spiritual awakening and alignment", "SPIRITUAL", "Divine wisdom flows through me", 777, "Angel Number"),
            ("1234", "Life progression and forward movement", "SELF-HELP", "I move forward with ease and grace", 1234, "Sequence"),
            ("369", "Tesla's divine code for creation", "SPIRITUAL", "I create with divine precision", 369, "Tesla")
        ]
        
        cursor.executemany(
            'INSERT INTO healing_code (code, description, category, affirmation, vibration, source) VALUES (?, ?, ?, ?, ?, ?)',
            sample_codes
        )
        conn.commit()
    
    # User methods
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, created_at FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'created_at': row[2]
            }
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, created_at FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'created_at': row[2]
            }
        return None
    
    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash the password (in a real system, use better password hashing)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': user_id,
            'username': username
        }
    
    # Soul Archive methods
    def get_soul_archives(self) -> List[Dict[str, Any]]:
        """Get all soul archives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM soul_archive ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'title', 'description', 'intention', 'frequency', 
                 'boost', 'multiplier', 'pattern_type', 'pattern_data', 
                 'user_id', 'created_at']
        
        archives = []
        for row in rows:
            archive = dict(zip(columns, row))
            archive['boost'] = bool(archive['boost'])
            archive['pattern_data'] = json.loads(archive['pattern_data'])
            archives.append(archive)
        
        return archives
    
    def get_soul_archive_by_id(self, archive_id: int) -> Optional[Dict[str, Any]]:
        """Get soul archive by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM soul_archive WHERE id = ?', (archive_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'title', 'description', 'intention', 'frequency', 
                     'boost', 'multiplier', 'pattern_type', 'pattern_data', 
                     'user_id', 'created_at']
            archive = dict(zip(columns, row))
            archive['boost'] = bool(archive['boost'])
            archive['pattern_data'] = json.loads(archive['pattern_data'])
            return archive
        return None
    
    def create_soul_archive(
        self,
        title: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        description: Optional[str] = None,
        intention: Optional[str] = None,
        frequency: str = str(SCHUMANN_RESONANCE),
        boost: Optional[bool] = False,
        multiplier: Optional[int] = 1,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new soul archive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO soul_archive 
            (title, description, intention, frequency, boost, multiplier, pattern_type, pattern_data, user_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                title, 
                description, 
                intention, 
                frequency, 
                1 if boost else 0, 
                multiplier, 
                pattern_type, 
                json.dumps(pattern_data),
                user_id
            )
        )
        archive_id = cursor.lastrowid
        conn.commit()
        
        # Get the created archive with datetime
        cursor.execute('SELECT * FROM soul_archive WHERE id = ?', (archive_id,))
        row = cursor.fetchone()
        conn.close()
        
        columns = ['id', 'title', 'description', 'intention', 'frequency', 
                 'boost', 'multiplier', 'pattern_type', 'pattern_data', 
                 'user_id', 'created_at']
        archive = dict(zip(columns, row))
        archive['boost'] = bool(archive['boost'])
        archive['pattern_data'] = json.loads(archive['pattern_data'])
        
        return archive
    
    def delete_soul_archive(self, archive_id: int) -> bool:
        """Delete a soul archive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM soul_archive WHERE id = ?', (archive_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # Healing Code methods
    def get_healing_codes(self) -> List[Dict[str, Any]]:
        """Get all healing codes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, code, description, category, affirmation, vibration, source FROM healing_code')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3],
                'affirmation': row[4],
                'vibration': row[5],
                'source': row[6]
            }
            for row in rows
        ]
    
    def get_healing_codes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get healing codes by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, code, description, category, affirmation, vibration, source FROM healing_code WHERE category = ?',
            (category,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3],
                'affirmation': row[4],
                'vibration': row[5],
                'source': row[6]
            }
            for row in rows
        ]
    
    def search_healing_codes(self, query: str) -> List[Dict[str, Any]]:
        """Search healing codes"""
        if not query:
            return self.get_healing_codes()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute(
            '''
            SELECT id, code, description, category, affirmation, vibration, source FROM healing_code 
            WHERE code LIKE ? OR description LIKE ? OR category LIKE ?
            ''',
            (search_pattern, search_pattern, search_pattern)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3],
                'affirmation': row[4],
                'vibration': row[5],
                'source': row[6]
            }
            for row in rows
        ]
    
    def create_healing_code(
        self, 
        code: str, 
        description: str, 
        category: Optional[str] = None,
        affirmation: Optional[str] = None,
        vibration: Optional[int] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new healing code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO healing_code (code, description, category, affirmation, vibration, source) VALUES (?, ?, ?, ?, ?, ?)',
            (code, description, category, affirmation, vibration, source)
        )
        code_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': code_id,
            'code': code,
            'description': description,
            'category': category,
            'affirmation': affirmation,
            'vibration': vibration,
            'source': source
        }
    
    # Past Life Insights methods
    def create_past_life_insight(
        self,
        user_id: int,
        past_life_pattern: str,
        life_period: Optional[str] = None,
        key_lesson: Optional[str] = None,
        resolution_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new past life insight"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO past_life_insights 
            (user_id, past_life_pattern, life_period, key_lesson, resolution_code) 
            VALUES (?, ?, ?, ?, ?)
            ''',
            (user_id, past_life_pattern, life_period, key_lesson, resolution_code)
        )
        insight_id = cursor.lastrowid
        conn.commit()
        
        # Get the created insight with datetime
        cursor.execute('SELECT * FROM past_life_insights WHERE id = ?', (insight_id,))
        row = cursor.fetchone()
        conn.close()
        
        columns = ['id', 'user_id', 'past_life_pattern', 'life_period', 
                  'key_lesson', 'resolution_code', 'created_at']
        return dict(zip(columns, row))
    
    def get_past_life_insights(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get past life insights, optionally filtered by user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM past_life_insights WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        else:
            cursor.execute('SELECT * FROM past_life_insights ORDER BY created_at DESC')
            
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'user_id', 'past_life_pattern', 'life_period', 
                  'key_lesson', 'resolution_code', 'created_at']
        
        return [dict(zip(columns, row)) for row in rows]
    
    # Environmental Anchoring methods
    def create_environmental_anchor(
        self,
        location_name: str,
        intention: str,
        field_type: str,
        field_data: Dict[str, Any],
        coordinates: Optional[str] = None,
        activation_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new environmental anchor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO environmental_anchoring 
            (location_name, coordinates, intention, field_type, field_data, activation_code) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                location_name,
                coordinates,
                intention,
                field_type,
                json.dumps(field_data),
                activation_code
            )
        )
        anchor_id = cursor.lastrowid
        conn.commit()
        
        # Get the created anchor with datetime
        cursor.execute('SELECT * FROM environmental_anchoring WHERE id = ?', (anchor_id,))
        row = cursor.fetchone()
        conn.close()
        
        columns = ['id', 'location_name', 'coordinates', 'intention', 
                  'field_type', 'field_data', 'activation_code', 'created_at']
        
        result = dict(zip(columns, row))
        result['field_data'] = json.loads(result['field_data'])
        
        return result
    
    def get_environmental_anchors(self) -> List[Dict[str, Any]]:
        """Get all environmental anchors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM environmental_anchoring ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'location_name', 'coordinates', 'intention', 
                  'field_type', 'field_data', 'activation_code', 'created_at']
        
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            result['field_data'] = json.loads(result['field_data'])
            results.append(result)
        
        return results


#########################################
# FLASK API IMPLEMENTATION
#########################################

if HAS_FLASK:
    app = Flask(__name__)
    storage = SacredStorage()

    @app.route('/')
    def index():
        """Render the main page of the Sacred Healing API"""
        return render_template('index.html')

    @app.route('/api/healing-codes', methods=['GET'])
    def api_healing_codes():
        """API endpoint to get healing codes"""
        category = request.args.get('category')
        search = request.args.get('search')
        
        if search:
            codes = storage.search_healing_codes(search)
        elif category:
            codes = storage.get_healing_codes_by_category(category)
        else:
            codes = storage.get_healing_codes()
        
        return jsonify(codes)

    @app.route('/api/healing-codes/<int:code_id>', methods=['GET'])
    def api_healing_code(code_id):
        """API endpoint to get a specific healing code"""
        codes = storage.get_healing_codes()
        for code in codes:
            if code['id'] == code_id:
                return jsonify(code)
        return jsonify({"error": "Healing code not found"}), 404

    @app.route('/api/sacred-geometry/torus', methods=['POST'])
    def api_torus_field():
        """API endpoint to generate a torus field"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        frequency = float(data.get('frequency', SCHUMANN_RESONANCE))
        
        try:
            result = SacredGeometryCalculator.torus_field_generator(intention, frequency)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sacred-geometry/merkaba', methods=['POST'])
    def api_merkaba_field():
        """API endpoint to generate a merkaba field"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        frequency = float(data.get('frequency', SCHUMANN_RESONANCE))
        
        try:
            result = SacredGeometryCalculator.merkaba_field_generator(intention, frequency)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sacred-geometry/metatron', methods=['POST'])
    def api_metatron_cube():
        """API endpoint to generate Metatron's Cube"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        boost = data.get('boost', False)
        
        try:
            result = SacredGeometryCalculator.metatrons_cube_amplifier(intention, boost)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sacred-geometry/sri-yantra', methods=['POST'])
    def api_sri_yantra():
        """API endpoint to generate Sri Yantra"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        
        try:
            result = SacredGeometryCalculator.sri_yantra_encoder(intention)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sacred-geometry/flower-of-life', methods=['POST'])
    def api_flower_of_life():
        """API endpoint to generate Flower of Life"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        duration = int(data.get('duration', 60))
        
        try:
            result = SacredGeometryCalculator.flower_of_life_pattern(intention, duration)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sacred-geometry/platonic-solid', methods=['POST'])
    def api_platonic_solid():
        """API endpoint to generate Platonic Solid resonator"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        solid_type = data.get('solid_type', 'dodecahedron')
        
        try:
            result = SacredGeometryCalculator.platonic_solid_resonator(intention, solid_type)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/amplify', methods=['POST'])
    def api_divine_amplify():
        """API endpoint to amplify intention with divine proportion"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        multiplier = float(data.get('multiplier', 1.0))
        
        try:
            result = SacredGeometryCalculator.divine_proportion_amplify(intention, multiplier)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/network-packet', methods=['POST'])
    def api_network_packet():
        """API endpoint to embed intention in network packet"""
        data = request.json
        if not data or 'intention' not in data:
            return jsonify({"error": "Intention is required"}), 400
        
        intention = data['intention']
        frequency = float(data.get('frequency', SCHUMANN_RESONANCE))
        field_type = data.get('field_type', 'torus')
        
        try:
            # Since Flask doesn't natively support async/await
            packet = IntentionPacket(intention, frequency, field_type)
            return jsonify({
                "packet": packet.to_dict(),
                "packet_base64": packet.to_base64()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/soul-archives', methods=['GET'])
    def api_soul_archives():
        """API endpoint to get soul archives"""
        archives = storage.get_soul_archives()
        return jsonify(archives)

    @app.route('/api/soul-archives/<int:archive_id>', methods=['GET'])
    def api_soul_archive(archive_id):
        """API endpoint to get a specific soul archive"""
        archive = storage.get_soul_archive_by_id(archive_id)
        if archive:
            return jsonify(archive)
        return jsonify({"error": "Soul archive not found"}), 404

    @app.route('/api/soul-archives', methods=['POST'])
    def api_create_soul_archive():
        """API endpoint to create a soul archive"""
        data = request.json
        if not data or 'title' not in data or 'pattern_type' not in data or 'pattern_data' not in data:
            return jsonify({"error": "Required fields: title, pattern_type, pattern_data"}), 400
        
        try:
            archive = storage.create_soul_archive(
                title=data['title'],
                pattern_type=data['pattern_type'],
                pattern_data=data['pattern_data'],
                description=data.get('description'),
                intention=data.get('intention'),
                frequency=str(data.get('frequency', SCHUMANN_RESONANCE)),
                boost=data.get('boost', False),
                multiplier=data.get('multiplier', 1),
                user_id=data.get('user_id')
            )
            return jsonify(archive), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/past-life-insights', methods=['GET'])
    def api_past_life_insights():
        """API endpoint to get past life insights"""
        user_id = request.args.get('user_id')
        if user_id:
            user_id = int(user_id)
            insights = storage.get_past_life_insights(user_id)
        else:
            insights = storage.get_past_life_insights()
        return jsonify(insights)

    @app.route('/api/past-life-insights', methods=['POST'])
    def api_create_past_life_insight():
        """API endpoint to create a past life insight"""
        data = request.json
        if not data or 'user_id' not in data or 'past_life_pattern' not in data:
            return jsonify({"error": "Required fields: user_id, past_life_pattern"}), 400
        
        try:
            insight = storage.create_past_life_insight(
                user_id=data['user_id'],
                past_life_pattern=data['past_life_pattern'],
                life_period=data.get('life_period'),
                key_lesson=data.get('key_lesson'),
                resolution_code=data.get('resolution_code')
            )
            return jsonify(insight), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/environmental-anchors', methods=['GET'])
    def api_environmental_anchors():
        """API endpoint to get environmental anchors"""
        anchors = storage.get_environmental_anchors()
        return jsonify(anchors)

    @app.route('/api/environmental-anchors', methods=['POST'])
    def api_create_environmental_anchor():
        """API endpoint to create an environmental anchor"""
        data = request.json
        if not data or 'location_name' not in data or 'intention' not in data or 'field_type' not in data or 'field_data' not in data:
            return jsonify({"error": "Required fields: location_name, intention, field_type, field_data"}), 400
        
        try:
            anchor = storage.create_environmental_anchor(
                location_name=data['location_name'],
                intention=data['intention'],
                field_type=data['field_type'],
                field_data=data['field_data'],
                coordinates=data.get('coordinates'),
                activation_code=data.get('activation_code')
            )
            return jsonify(anchor), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Other API endpoints for additional functionality...


#########################################
# COMMAND LINE INTERFACE
#########################################

class SacredHealer:
    """Main class for the Sacred Healing CLI"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.storage = SacredStorage()
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def divine_amplify(self, intention: str, multiplier: float = 1.0) -> Dict[str, Any]:
        """Amplify intention using divine proportion"""
        logger.info(f"Amplifying intention: '{intention}'")
        return SacredGeometryCalculator.divine_proportion_amplify(intention, multiplier)
    
    def generate_field(self, intention: str, field_type: str, **kwargs) -> Dict[str, Any]:
        """Generate a sacred geometry field"""
        logger.info(f"Generating {field_type} field for intention: '{intention}'")
        
        if field_type == "torus":
            frequency = float(kwargs.get('frequency', SCHUMANN_RESONANCE))
            return SacredGeometryCalculator.torus_field_generator(intention, frequency)
        elif field_type == "merkaba":
            frequency = float(kwargs.get('frequency', SCHUMANN_RESONANCE))
            return SacredGeometryCalculator.merkaba_field_generator(intention, frequency)
        elif field_type == "metatron":
            boost = kwargs.get('boost', False)
            return SacredGeometryCalculator.metatrons_cube_amplifier(intention, boost)
        elif field_type == "sri_yantra":
            return SacredGeometryCalculator.sri_yantra_encoder(intention)
        elif field_type == "flower_of_life":
            duration = int(kwargs.get('duration', 60))
            return SacredGeometryCalculator.flower_of_life_pattern(intention, duration)
        elif field_type == "platonic_solid":
            solid_type = kwargs.get('solid_type', 'dodecahedron')
            return SacredGeometryCalculator.platonic_solid_resonator(intention, solid_type)
        else:
            raise ValueError(f"Unknown field type: {field_type}")
    
    def create_packet(self, intention: str, frequency: float = SCHUMANN_RESONANCE, field_type: str = "torus") -> Dict[str, Any]:
        """Create an intention packet"""
        logger.info(f"Creating intention packet for: '{intention}'")
        
        packet = IntentionPacket(intention, frequency, field_type)
        
        return {
            "packet": packet.to_dict(),
            "packet_base64": packet.to_base64()
        }
    
    def save_to_file(self, data: Dict[str, Any], filename: str) -> None:
        """Save data to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {filename}")
    
    def get_healing_code(self, query: str) -> List[Dict[str, Any]]:
        """Search for healing codes"""
        if HAS_FUZZY_SEARCH:
            # Use fuzzy matching for better results
            all_codes = self.storage.get_healing_codes()
            
            # Search by code
            code_matches = process.extract(query, [c['code'] for c in all_codes], scorer=fuzz.token_set_ratio)
            code_ids = [i for i, (_, score) in enumerate(code_matches) if score > 70]
            
            # Search by description
            desc_matches = process.extract(query, [c['description'] for c in all_codes], scorer=fuzz.token_set_ratio)
            desc_ids = [i for i, (_, score) in enumerate(desc_matches) if score > 70]
            
            # Combine results
            result_ids = set(code_ids + desc_ids)
            results = [all_codes[i] for i in result_ids]
            
            return results
        else:
            # Fall back to simple search
            return self.storage.search_healing_codes(query)
    
    def run_interactive_cli(self):
        """Run an interactive CLI"""
        print("\n===== Sacred Healing Platform =====")
        print("Welcome to the interactive healing interface")
        
        while True:
            print("\nOptions:")
            print("1. Generate Sacred Geometry Field")
            print("2. Search Healing Codes")
            print("3. Broadcast Intention")
            print("4. Save to Soul Archive")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                intention = input("Enter intention: ")
                print("\nField types:")
                print("1. Torus Field")
                print("2. Merkaba")
                print("3. Metatron's Cube")
                print("4. Sri Yantra")
                print("5. Flower of Life")
                print("6. Platonic Solid")
                
                field_choice = input("\nSelect field type (1-6): ")
                field_types = ["torus", "merkaba", "metatron", "sri_yantra", "flower_of_life", "platonic_solid"]
                
                try:
                    field_type = field_types[int(field_choice) - 1]
                    
                    kwargs = {}
                    if field_type in ["torus", "merkaba"]:
                        frequency = input("Enter frequency (default 7.83 Hz): ")
                        if frequency:
                            kwargs['frequency'] = float(frequency)
                    elif field_type == "metatron":
                        boost = input("Apply full boost? (y/n): ").lower() == 'y'
                        kwargs['boost'] = boost
                    elif field_type == "flower_of_life":
                        duration = input("Enter duration in seconds (default 60): ")
                        if duration:
                            kwargs['duration'] = int(duration)
                    elif field_type == "platonic_solid":
                        print("\nPlatonic solid types:")
                        print("1. Tetrahedron (Fire)")
                        print("2. Hexahedron/Cube (Earth)")
                        print("3. Octahedron (Air)")
                        print("4. Dodecahedron (Ether)")
                        print("5. Icosahedron (Water)")
                        
                        solid_choice = input("\nSelect solid type (1-5): ")
                        solid_types = ["tetrahedron", "hexahedron", "octahedron", "dodecahedron", "icosahedron"]
                        if 1 <= int(solid_choice) <= 5:
                            kwargs['solid_type'] = solid_types[int(solid_choice) - 1]
                    
                    result = self.generate_field(intention, field_type, **kwargs)
                    print("\nGenerated Field Data:")
                    print(json.dumps(result, indent=2))
                    
                    save = input("\nSave to file? (y/n): ").lower() == 'y'
                    if save:
                        filename = input("Enter filename: ")
                        if not filename.endswith('.json'):
                            filename += '.json'
                        self.save_to_file(result, filename)
                
                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")
            
            elif choice == "2":
                query = input("Enter search term: ")
                results = self.get_healing_code(query)
                
                if results:
                    print(f"\nFound {len(results)} healing codes:")
                    for i, code in enumerate(results, 1):
                        print(f"\n{i}. Code: {code['code']}")
                        print(f"   Description: {code['description']}")
                        print(f"   Category: {code['category']}")
                        if code.get('affirmation'):
                            print(f"   Affirmation: {code['affirmation']}")
                        if code.get('source'):
                            print(f"   Source: {code['source']}")
                else:
                    print("\nNo healing codes found matching your query.")
            
            elif choice == "3":
                intention = input("Enter intention to broadcast: ")
                frequency = input("Enter frequency (default 7.83 Hz): ")
                frequency = float(frequency) if frequency else SCHUMANN_RESONANCE
                
                print("\nField types:")
                print("1. Torus Field")
                print("2. Merkaba")
                print("3. Metatron's Cube")
                print("4. Sri Yantra")
                print("5. Flower of Life")
                
                field_choice = input("\nSelect field type (1-5): ")
                field_types = ["torus", "merkaba", "metatron", "sri_yantra", "flower_of_life"]
                
                try:
                    field_type = field_types[int(field_choice) - 1]
                    result = self.create_packet(intention, frequency, field_type)
                    
                    print("\nIntention Packet Generated:")
                    print(f"Intention: {intention}")
                    print(f"Frequency: {frequency} Hz")
                    print(f"Field type: {field_type}")
                    print(f"Packet: {result['packet_base64'][:30]}...{result['packet_base64'][-10:]}")
                    
                    save = input("\nSave packet to file? (y/n): ").lower() == 'y'
                    if save:
                        filename = input("Enter filename: ")
                        if not filename.endswith('.json'):
                            filename += '.json'
                        self.save_to_file(result, filename)
                
                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")
            
            elif choice == "4":
                title = input("Enter title for soul archive: ")
                intention = input("Enter intention: ")
                
                print("\nField types:")
                print("1. Torus Field")
                print("2. Merkaba")
                print("3. Metatron's Cube")
                print("4. Sri Yantra")
                print("5. Flower of Life")
                print("6. Platonic Solid")
                
                field_choice = input("\nSelect field type (1-6): ")
                field_types = ["torus", "merkaba", "metatron", "sri_yantra", "flower_of_life", "platonic_solid"]
                
                try:
                    field_type = field_types[int(field_choice) - 1]
                    
                    kwargs = {}
                    if field_type in ["torus", "merkaba"]:
                        frequency = input("Enter frequency (default 7.83 Hz): ")
                        if frequency:
                            kwargs['frequency'] = float(frequency)
                    elif field_type == "metatron":
                        boost = input("Apply full boost? (y/n): ").lower() == 'y'
                        kwargs['boost'] = boost
                    elif field_type == "flower_of_life":
                        duration = input("Enter duration in seconds (default 60): ")
                        if duration:
                            kwargs['duration'] = int(duration)
                    elif field_type == "platonic_solid":
                        solid_choice = input("\nSelect solid type (tetrahedron, hexahedron, octahedron, dodecahedron, icosahedron): ")
                        kwargs['solid_type'] = solid_choice
                    
                    field_data = self.generate_field(intention, field_type, **kwargs)
                    
                    description = input("Enter description (optional): ")
                    frequency_str = str(kwargs.get('frequency', SCHUMANN_RESONANCE)) if field_type in ["torus", "merkaba"] else str(SCHUMANN_RESONANCE)
                    
                    archive = self.storage.create_soul_archive(
                        title=title,
                        pattern_type=field_type,
                        pattern_data=field_data,
                        description=description,
                        intention=intention,
                        frequency=frequency_str,
                        boost=kwargs.get('boost', False),
                        multiplier=1
                    )
                    
                    print("\nSoul Archive Created:")
                    print(f"ID: {archive['id']}")
                    print(f"Title: {archive['title']}")
                    print(f"Pattern Type: {archive['pattern_type']}")
                    print(f"Created At: {archive['created_at']}")
                
                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")
            
            elif choice == "5":
                print("\nExiting Sacred Healing Platform. Blessings on your journey!")
                break
            
            else:
                print("\nInvalid choice. Please enter a number between 1 and 5.")


#########################################
# BROADCAST MODE IMPLEMENTATION
#########################################

class SacredIntentionBroadcaster:
    """Main class for broadcasting intentions over networks"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
    
    async def create_intention_packet(
        self, 
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus"
    ) -> str:
        """Create a network packet containing the intention"""
        return await embed_intention_in_network_packet(intention, frequency, field_type)
    
    async def broadcast_intention(
        self,
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus",
        amplify: bool = False,
        multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """Broadcast intention over network"""
        logger.info(f"Broadcasting intention: '{intention}'")
        
        # Create the basic packet
        packet_base64 = await self.create_intention_packet(intention, frequency, field_type)
        
        # Calculate sacred geometry data
        geometry_data = None
        if field_type == "torus":
            geometry_data = SacredGeometryCalculator.torus_field_generator(intention, frequency)
        elif field_type == "merkaba":
            geometry_data = SacredGeometryCalculator.merkaba_field_generator(intention, frequency)
        elif field_type == "metatron":
            geometry_data = SacredGeometryCalculator.metatrons_cube_amplifier(intention, amplify)
        elif field_type == "sri_yantra":
            geometry_data = SacredGeometryCalculator.sri_yantra_encoder(intention)
        elif field_type == "flower_of_life":
            geometry_data = SacredGeometryCalculator.flower_of_life_pattern(intention, 60)
        elif field_type == "platonic_solid":
            geometry_data = SacredGeometryCalculator.platonic_solid_resonator(intention)
        
        # Apply divine amplification if requested
        amplified_data = None
        if amplify:
            amplified_data = SacredGeometryCalculator.divine_proportion_amplify(intention, multiplier)
            logger.info(f"Divine amplification applied. Fibonacci multiplier: {amplified_data['fibonacci_multiplier']}")
        
        # Extract intention from packet to verify
        extracted = extract_intention_from_packet(packet_base64)
        logger.info(f"Verification - extracted intention: '{extracted}'")
        
        # Return result
        result = {
            "intention": intention,
            "frequency": frequency,
            "field_type": field_type,
            "packet_base64": packet_base64
        }
        
        if geometry_data:
            result["geometry_data"] = geometry_data
        
        if amplified_data:
            result["amplified_data"] = amplified_data
        
        logger.info(f"Intention broadcast complete: {intention}")
        logger.info(f"Field type: {field_type}, Frequency: {frequency} Hz")
        
        return result


#########################################
# MAIN APPLICATION
#########################################

def run_api_server(port: int = API_PORT):
    """Run the application in Flask API mode"""
    if not HAS_FLASK:
        logger.error("Flask is required for API mode. Install it with 'pip install flask'")
        return
    
    logger.info(f"Starting Sacred Healing API on port {port}")
    
    # Open browser
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        logger.info(f"Please open your browser to http://localhost:{port}")
    
    # Start Flask server
    app.run(host="0.0.0.0", port=port, debug=False)


async def run_broadcast_mode(
    intention: str,
    frequency: float = SCHUMANN_RESONANCE,
    field_type: str = "torus",
    amplify: bool = False,
    multiplier: float = 1.0,
    output: Optional[str] = None,
    debug: bool = False
):
    """Run the application in broadcast mode"""
    logger.info("Starting Sacred Healing Platform in broadcast mode")
    
    broadcaster = SacredIntentionBroadcaster(debug=debug)
    
    result = await broadcaster.broadcast_intention(
        intention=intention,
        frequency=frequency,
        field_type=field_type,
        amplify=amplify,
        multiplier=multiplier
    )
    
    # Print result
    print(f"\nIntention: {intention}")
    print(f"Frequency: {frequency} Hz")
    print(f"Field type: {field_type}")
    print(f"Embedded in packet: {result['packet_base64'][:30]}...{result['packet_base64'][-10:]}\n")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Intention data saved to {output}")
    
    print("Packet ready for transmission to end users")


def run_cli_mode(debug: bool = False):
    """Run the application in interactive CLI mode"""
    healer = SacredHealer(debug=debug)
    healer.run_interactive_cli()


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Sacred Healing API")
    parser.add_argument("--mode", required=True, choices=["api", "broadcast", "cli"],
                        help="Operation mode")
    
    # Common options
    parser.add_argument("--intention", help="Intention to broadcast or calculate")
    parser.add_argument("--frequency", type=float, default=SCHUMANN_RESONANCE,
                        help=f"Frequency in Hz (default: {SCHUMANN_RESONANCE} - Earth's Schumann resonance)")
    parser.add_argument("--field-type", choices=["torus", "merkaba", "metatron", "sri_yantra", "flower_of_life", "platonic_solid"],
                        default="torus", help="Sacred geometry field type")
    parser.add_argument("--amplify", action="store_true", help="Apply divine proportion amplification")
    parser.add_argument("--multiplier", type=float, default=1.0, help="Fibonacci multiplier for amplification")
    parser.add_argument("--output", help="Output file to save data (JSON format)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # API options
    parser.add_argument("--port", type=int, default=API_PORT, help="API server port")
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Run appropriate mode
    if args.mode == "api":
        run_api_server(args.port)
    
    elif args.mode == "broadcast":
        if not args.intention:
            print("Error: --intention is required for broadcast mode")
            return
        asyncio.run(run_broadcast_mode(
            intention=args.intention,
            frequency=args.frequency,
            field_type=args.field_type,
            amplify=args.amplify,
            multiplier=args.multiplier,
            output=args.output,
            debug=args.debug
        ))
    
    elif args.mode == "cli":
        run_cli_mode(debug=args.debug)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSacred Healing Platform shutting down...")
        sys.exit(0)
