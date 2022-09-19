import re

# CPU PATTERNS ==================================================================================================
INTEL_I_MODEL_PATTERN = re.compile(r"(i\d)([-\s]{0,1}\d{3,5}\w{0,2})?", re.IGNORECASE)
INTEL_CORE_PATTERN = re.compile(r"core\s?2\s?(duo|quad)", re.IGNORECASE)
INTEL_CELERON_PATTERN = re.compile(r"celeron\s(\S{3,5}\s)", re.IGNORECASE)
INTEL_PENTIUM_PATTERN = re.compile(r"pentium\s\S{3,5}", re.IGNORECASE)
AMD_RYZEN_PATTERN = re.compile(r"Ryzen\s\d[\s-]\S{4,5}", re.IGNORECASE)
AMD_FX_PATTERN = re.compile(r"FX[\s-]\d{3,4}", re.IGNORECASE)
# =================================================================================================================

# GPU PATTERNS =====================================================================================================
# ==================================================================================================================

# SYSTEM MEMORY PATTERN ============================================================================================
# ==================================================================================================================

def load_json_file(fileName: str) -> dict:
    pass

def walk_game_obj(game: dict) -> dict:
    pass

def check_cpu(cpuString: str) -> str:
    pass

def check_gpu(gpuString: str) -> str:
    pass

def check_memory(memoryString: str) -> str:
    pass

def main():
    pass

if __name__ == '__main__':
    main()