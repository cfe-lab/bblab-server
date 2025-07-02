# This module is compatible with python 3.7 #

import subprocess
import tempfile
import os


def get_qvalues(pvalues):
    """
    This function uses the r script to convert a list of pvalues into
    a list of qvalues.

    Depends On: R
    """
    # v2025-07-02c: Maximum debug output for R script interaction
    # print(f"[DEBUG] get_qvalues called with {len(pvalues)} p-values")
    # print(f"[DEBUG] Raw p-values: {pvalues}")

    # Input validation and cleaning
    if not pvalues:
        # print("[DEBUG] No p-values provided, returning empty list")
        return []

    # Clean and validate p-values - be extremely defensive
    cleaned_pvalues = []
    for i, pval in enumerate(pvalues):
        try:
            # Convert to float and validate
            if pval is None:
                # print(f"[DEBUG] P-value at index {i} is None, using fallback 1.0")
                pval_float = 1.0  # Conservative fallback
            elif isinstance(pval, str):
                try:
                    pval_float = float(pval)
                    # print(f"[DEBUG] P-value at index {i}: '{pval}' -> {pval_float}")
                except (ValueError, TypeError):
                    # print(f"[DEBUG] P-value at index {i}: '{pval}' could not be converted, using fallback 1.0")
                    pval_float = 1.0  # Conservative fallback
            else:
                pval_float = float(pval)
                # print(f"[DEBUG] P-value at index {i}: {pval} -> {pval_float}")

            # Check for invalid values
            import math

            if (
                math.isnan(pval_float)
                or math.isinf(pval_float)
                or pval_float < 0
                or pval_float > 1
            ):
                # print(f"[DEBUG] P-value at index {i}: {pval_float} is invalid, using fallback 1.0")
                pval_float = 1.0  # Conservative fallback

            cleaned_pvalues.append(pval_float)

        except Exception as e:
            # Any error - use conservative fallback
            # print(f"[DEBUG] P-value at index {i}: Exception {e}, using fallback 1.0")
            cleaned_pvalues.append(1.0)

    # print(f"[DEBUG] After cleaning: {len(cleaned_pvalues)} valid p-values: {cleaned_pvalues}")

    # Final validation - ensure we have valid p-values
    for pval in cleaned_pvalues:
        if not isinstance(pval, (int, float)) or pval < 0 or pval > 1:
            raise ValueError(
                f"Invalid p-value after cleaning: {pval}. All p-values must be numeric and in range [0,1]"
            )

    # This block runs the R script from the using the commandline and converts the console output into a list.
    qvalues = []
    r_script_path = "{}qvalue_calculate.r".format(
        os.environ.get("BBLAB_R_PATH", "fail")
    )
    r_input = str(cleaned_pvalues)

    # print(f"[DEBUG] R script path: {r_script_path}")
    # print(f"[DEBUG] R script input: {r_input}")
    # print(f"[DEBUG] R script input type: {type(r_input)}")
    # print(f"[DEBUG] R script input length: {len(r_input)}")

    with tempfile.TemporaryFile() as tmpf:
        proc = subprocess.Popen(
            ["Rscript", r_script_path, r_input], stdout=tmpf, stderr=subprocess.PIPE
        )
        _, stderr = proc.communicate()

        # print(f"[DEBUG] R script return code: {proc.returncode}")

        # Check for R script errors
        if proc.returncode != 0:
            stderr_msg = stderr.decode("utf-8") if stderr else "Unknown error"
            print(f"[ERROR] R script failed with return code {proc.returncode}")
            print(f"[ERROR] R script stderr: {stderr_msg}")
            raise RuntimeError(
                f"R script failed with return code {proc.returncode}. Input p-values: {cleaned_pvalues}. Error: {stderr_msg}"
            )

        tmpf.seek(0)
        raw_output = tmpf.read().decode("utf-8").strip()

        # print(f"[DEBUG] R script raw output length: {len(raw_output)}")
        # print(f"[DEBUG] R script raw output (repr): {repr(raw_output)}")
        # print(f"[DEBUG] R script raw output (formatted): '{raw_output}'")
        # print(f"[DEBUG] R script stderr content: '{stderr.decode('utf-8') if stderr else 'None'}'")

        # Handle empty output
        if not raw_output:
            print(
                f"[ERROR] R script produced no output for input p-values: {cleaned_pvalues}"
            )
            raise RuntimeError(
                f"R script produced no output for input p-values: {cleaned_pvalues}"
            )

        # Robust parsing: handle different R output formats
        # R script returns space-separated values with a trailing comma: "0.1 0.2 0.3 ,"
        if raw_output.endswith(","):
            # Space-separated format with trailing comma
            # print("[DEBUG] Parsing output as space-separated values with trailing comma")
            # Remove trailing comma and split by space
            clean_output = raw_output.rstrip(",").strip()
            qvalue_strings = clean_output.split()
        elif "," in raw_output and " " not in raw_output:
            # Pure comma-separated format (no spaces): "0.1,0.2,0.3"
            # print("[DEBUG] Parsing output as comma-separated values")
            qvalue_strings = raw_output.split(",")
        else:
            # Space-separated format (old R versions): "0.1 0.2 0.3"
            # print("[DEBUG] Parsing output as space-separated values")
            qvalue_strings = raw_output.split()

        # print(f"[DEBUG] Split into {len(qvalue_strings)} parts: {qvalue_strings}")

        # Convert to floats, filtering empty strings
        qvalues = []
        for j, qstr in enumerate(qvalue_strings):
            qstr = qstr.strip()
            # print(f"[DEBUG] Processing q-value string {j}: '{qstr}'")
            if qstr:
                try:
                    qval = float(qstr)
                    # print(f"[DEBUG] Converted q-value {j}: '{qstr}' -> {qval}")
                    qvalues.append(qval)
                except ValueError as e:
                    # Skip invalid values but log the issue
                    print(
                        f"[ERROR] Could not convert q-value {j}: '{qstr}' (error: {e})"
                    )
                    continue

        # print(f"[DEBUG] Final parsed q-values: {qvalues}")

        # Validate that we got the expected number of q-values
        if len(qvalues) != len(cleaned_pvalues):
            print(
                f"[ERROR] R script returned {len(qvalues)} q-values but expected {len(cleaned_pvalues)}"
            )
            print(f"[ERROR] Input p-values ({len(cleaned_pvalues)}): {cleaned_pvalues}")
            print(f"[ERROR] Output q-values ({len(qvalues)}): {qvalues}")
            raise RuntimeError(
                f"R script returned {len(qvalues)} q-values but expected {len(cleaned_pvalues)} (input p-values: {len(cleaned_pvalues)})"
            )

    # print(f"[DEBUG] Returning {len(qvalues)} q-values: {qvalues}")
    return qvalues
