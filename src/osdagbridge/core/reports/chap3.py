# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_FORCE_LONGITUDINAL,
    KEY_SL_FORCE_TRANSVERSE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value


def _seismic_force(value):
    """Format a computed seismic force for Table 3.6, with an explicit fallback."""
    if value in (None, ""):
        return "N/A"
    try:
        return f"{float(value):.2f} kN"
    except (TypeError, ValueError):
        return "N/A"


def ch3_loads(input_dict):
    # Vehicle live loads follow exactly what is selected in the Loading tab
    # of Additional Inputs (KEY_LL_* flags). One table row per selected class.
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    # Braking force (IRC 6 Cl. 211.2) is a function of the number of design
    # lanes. The UI lane-count key is not always populated, so derive the
    # count from the carriageway width using IRC 6 Table 6 as a fallback.
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_lanes_source = "lane count input"
    if lanes in (None, ""):
        carriageway = input_dict.get(KEY_CARRIAGEWAY_WIDTH)
        if carriageway not in (None, ""):
            try:
                lanes = IRC6_2017.table_6(float(carriageway))
                braking_lanes_source = "carriageway width (IRC 6 Table 6)"
            except Exception:
                lanes = None
    braking_str = "N/A"
    if lanes not in (None, ""):
        try:
            braking_kN = IRC6_2017.cl_211_2_braking_force(int(lanes)) * 9.81
            braking_str = f"{braking_kN:.2f}"
        except Exception:
            pass

    span = input_dict.get(KEY_SPAN)
    factor_a = factor_heavy = None
    if span not in (None, ""):
        try:
            span_m = float(span)
            factor_a = 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
            factor_heavy = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
        except Exception:
            pass

    vehicle_specs = [
        (KEY_LL_IRC_CLASS_A,      "Class A",             factor_a,    "IRC 6 Cl. 208.2"),
        (KEY_LL_IRC_70R_WHEELED,  "Class 70R (Wheeled)", factor_heavy, "IRC 6 Cl. 208.3"),
        (KEY_LL_IRC_70R_TRACKED,  "Class 70R (Tracked)", factor_heavy, "IRC 6 Cl. 208.3"),
        (KEY_LL_IRC_70R_BOGIE,    "Class 70R (Bogie)",   factor_heavy, "IRC 6 Cl. 208.3"),
        (KEY_LL_IRC_AA_WHEELED,   "Class AA (Wheeled)",  factor_heavy, "IRC 6 Cl. 208.3"),
        (KEY_LL_IRC_AA_TRACKED,   "Class AA (Tracked)",  factor_heavy, "IRC 6 Cl. 208.3"),
        (KEY_LL_IRC_CLASS_SV,     "Class SV",            None,         "IRC 6 Cl. 208"),
        (KEY_LL_IRC_CLASS_FATIGUE,"Class Fatigue",       None,         "IRC 6 Cl. 219"),
    ]

    def _vehicle_row(name, factor, clause):
        factor_tex = f"{factor:.3f}" if factor is not None else "N/A"
        return (r"\textnormal{" + _tex(name) + r"} & " + factor_tex
                + r" & " + braking_str + r" & \footnotesize N/A & " + _tex(clause)
                + r" \\[6pt]" + "\n" + r"\hline")

    vehicle_rows = [
        _vehicle_row(name, factor, clause)
        for key, name, factor, clause in vehicle_specs
        if input_dict.get(key)
    ]
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for item in custom:
            if isinstance(item, dict) and item.get('name'):
                vehicle_rows.append(_vehicle_row(item['name'], None, "User defined"))
            elif isinstance(item, str):
                vehicle_rows.append(_vehicle_row(item, None, "User defined"))
    if not vehicle_rows:
        vehicle_rows.append(_vehicle_row("None", None, "---"))
    vehicle_rows_str = "\n".join(vehicle_rows)

    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_str = (f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m"
                      r"\textsuperscript{2}" + " (IRC 6 Cl. 206.1)")
        except Exception:
            fp_str = "N/A"
    elif fp_value not in (None, ""):
        fp_str = f"{fp_value} kN/m" + r"\textsuperscript{2}"
    else:
        fp_str = "N/A"

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table.

        Labels are restricted to the known IRC load aliases and numeric factors
        are parsed explicitly, so unexpected internal names (for example
        ``EQ_X``) or stray LaTeX/brackets cannot leak into the rendered table.
        """
        def _number(value):
            if value is None:
                return '--'
            try:
                return f"{float(value):.2f}"
            except (TypeError, ValueError):
                return '--'

        parts = []
        for load, val in factors.items():
            key = str(load).strip().lower()
            if key.startswith("eq") or "seismic" in key:
                label = "EQ"
            else:
                label = _LOAD_LABEL_MAP.get(key, key.upper())
            label = ''.join(ch for ch in label if ch.isalnum())
            if not label:
                continue
            if isinstance(val, dict):  # permanent load with adding/relieving
                parts.append(
                    f"{label}({_number(val.get('adding'))}/{_number(val.get('relieving'))})"
                )
            else:
                if val is None:
                    continue  # skip N/A factors
                try:
                    parts.append(f"{label}({float(val):.2f})")
                except (TypeError, ValueError):
                    continue
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load -- Self Weight}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{3.8cm}|C{2.1cm}|C{2.2cm}|L{3.6cm}|L{3.0cm}|}
\caption{\textbf{Vehicle Live Loads (LL) --- IRC 6:2017}}
\hline
\textbf{Vehicle Class} & \textbf{Impact Factor} & \textbf{Braking (kN)} & \textbf{Centrifugal (kN)} & \textbf{Clause} \\[6pt]
\hline
""" + vehicle_rows_str + r"""
\textnormal{All selected vehicles} & --- & """ + braking_str + r""" & \footnotesize N/A (no curvature) & \textnormal{IRC 6 Cl. 211.2} \\[6pt]
\hline
\end{longtable}

\noindent\textit{Note: Vehicle classes are taken directly from the Loading tab of Additional Inputs. Centrifugal load is N/A because the model has no horizontal-curvature input. Braking is the total design braking force for the selected lanes (IRC 6 Cl. 211.2); the same value applies to every vehicle row and is not a per-vehicle load. The lane count was derived from """ + _tex(braking_lanes_source) + r""".}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Footpath Live Load (Footway) --- IRC 6:2017}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Pressure Input Mode} & """ + _tex(fp_mode or "N/A") + r""" \\[6pt]
\hline
\textnormal{Design Footway Load} & """ + fp_str + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + _seismic_force(input_dict.get(KEY_SL_FORCE_LONGITUDINAL)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + _seismic_force(input_dict.get(KEY_SL_FORCE_TRANSVERSE)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
\caption{\textbf{Load Combinations}}
\hline
\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]
\hline
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


