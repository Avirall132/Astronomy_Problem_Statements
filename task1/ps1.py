from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits


START_UTC = "2022-04-15T05:36:40"
END_UTC = "2022-04-15T05:38:16"
TARGET_LAT = 57.51
TARGET_LON = 78.14

FITS_FILE = Path(
    r"C:\Users\invet\OneDrive\Desktop\Inter-IIT\Datasets\ch2_xsm_20220415_v1\xsm\data\2022\04\15\raw\ch2_xsm_20220415_v1_level1.fits"
)


def normalize_utc(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip().str.replace("Z", "", regex=False)
    return pd.to_datetime(text, utc=True, errors="coerce")


def angular_distance_deg(lat1: float, lon1: float, lat2: pd.Series, lon2: pd.Series) -> pd.Series:
    lat1r = np.radians(lat1)
    lon1r = np.radians(lon1)
    lat2r = np.radians(lat2.to_numpy(dtype=float))
    lon2r = np.radians(lon2.to_numpy(dtype=float))

    cosang = np.sin(lat1r) * np.sin(lat2r) + np.cos(lat1r) * np.cos(lat2r) * np.cos(lon1r - lon2r)
    cosang = np.clip(cosang, -1.0, 1.0)
    return pd.Series(np.degrees(np.arccos(cosang)), index=lat2.index)


def main() -> None:
    if not FITS_FILE.exists():
        print(f"File not found: {FITS_FILE}")
        print("The current workspace only has 2020-05-29 raw files.")
        return

    with fits.open(FITS_FILE) as hdul:
        df = hdul[1].data.to_pandas()

    if "UTCSTRING" in df.columns:
        df["UTC"] = normalize_utc(df["UTCSTRING"])
    elif "TIME" in df.columns:
        # TIME is UTC seconds from 2017-01-01 00:00:00.
        epoch = pd.Timestamp("2017-01-01T00:00:00Z")
        df["UTC"] = epoch + pd.to_timedelta(df["TIME"], unit="s")
    else:
        raise ValueError("No UTCSTRING or TIME column found in FITS table")

    start = pd.Timestamp(START_UTC, tz="UTC")
    end = pd.Timestamp(END_UTC, tz="UTC")

    time_slice = df[(df["UTC"] >= start) & (df["UTC"] <= end)].copy()
    print(f"Rows in UTC window [{START_UTC}Z, {END_UTC}Z]: {len(time_slice)}")

    if len(time_slice) == 0:
        print("No records found in this time interval.")
        return

    print("Available columns in this file:")
    print(list(time_slice.columns))

    lat_cols = [c for c in time_slice.columns if "lat" in str(c).lower()]
    lon_cols = [c for c in time_slice.columns if "lon" in str(c).lower()]

    if lat_cols and lon_cols:
        lat_col = lat_cols[0]
        lon_col = lon_cols[0]
        dist = angular_distance_deg(TARGET_LAT, TARGET_LON, time_slice[lat_col], time_slice[lon_col])
        nearest_idx = dist.idxmin()

        print(f"Using coordinate columns: {lat_col}, {lon_col}")
        print(f"Nearest row to ({TARGET_LAT}, {TARGET_LON}) has angular distance {dist.loc[nearest_idx]:.6f} deg")
        print(time_slice.loc[[nearest_idx]].to_string(index=False))
    else:
        print("No latitude/longitude columns are present in this XSM level1 FITS table.")
        print("To filter by latitude/longitude, join this time_slice with a spacecraft ephemeris/orbit file using UTC.")
        print("Then compute nearest point to (57.51, 78.14) in that joined table.")


if __name__ == "__main__":
    main()

