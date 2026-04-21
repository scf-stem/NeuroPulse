"""
Tremor Guard - Tremor Models (Alias)
震颤卫士 - 震颤模型别名

This file re-exports from tremor_data.py for backward compatibility.
"""

from app.models.tremor_data import TremorSession, TremorData

__all__ = ['TremorSession', 'TremorData']
