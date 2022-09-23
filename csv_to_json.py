from argparse import ArgumentParser
import re
import csv
import sys, os
import json

PROCESSOR_CSV = None
FAMILY_CSV = None
ARCHITECTURE_CSV = None

INPUT_FILE_NAME = None
OUTPUT_FILE_NAME = "./data/cpus.json"

PROCESSORS_OBJ = {}
#=================================================================================================
MANUFACTURERE = {
    1: "AMD",
    9: "INTEL"
}

FAMILY = {

}
#=================================================================================================
# POPULATE THE FAMILY OBJ ========================================================================
def step_1():
    try:
        for row in FAMILY_CSV:
            if (row[0] == "id"):
                continue

            print('=' * 100)

            print("ROW: {}".format(row))
            mID = int(row[1])
            print("MANU_ID: {}".format(mID))

            if(mID == 9 or mID == 1):
                fID = int(row[0])
                fName = row[2]

                FAMILY[fID] = fName

            print('=' * 100)

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(f"ERROR IN FAMILY POPULATION PROCESS: {E}")

# READ THE PROCESSOR CSV =========================================================================
def step_2():
    try:
        index = 0
        for row in PROCESSOR_CSV:
            mID = fID = model = cSpeed = tCount = cCount = mName = fName = None


            print(f"ROW> M:{row[3]} F:{row[4]} MO:{row[11]} CS:{row[13]} CC:{row[16]} TC:{row[15]}")
            if (row[0] == 'id'):
                continue

            # GET MANUFACTRURE ID
            mID = int(row[3])
            print(f"MID: {mID}")

            if(mID == 1 or mID == 9):
                # GET FAMITY ID
                try:
                    fID = int(row[4])
                except:
                    print(f"[-] CANT FETCH FAMILY ID: {row[4]}")

                # GET MODEL
                try:
                    model = row[11]
                    pattern = re.compile("i\d-")
                    model = re.sub(pattern, "", model)

                except:
                    print(f"[-] CANT FETCH MODEL: {row[11]}")

                # GET CLOCK SPEED
                try:
                    cSpeed = int(row[13])
                except:
                    print(f"[-] CANT FETCH CLOCK SPEED: {row[13]}")
                    cSpeed = 000

                # GET THREAD COUNT
                try:
                    tCount = int(row[15])
                except:
                    print(f"[-] CANT FETCH THREAD COUNT: {row[15]}")
                    tCount = 000

                # GET CORE COUNT
                try:
                    cCount = int(row[16])
                except:
                    print(f"[-] CANT FETCH CORE COUNT: {row[16]}")
                    cCount = 000

                # FETCH MANFUACTURER NAME FROM MANUFACTURER OBJ
                mName = MANUFACTURERE[mID]
                # FETCH FAMILY NAME FROM FAMILY OBJ
                fName = FAMILY[fID]

                # CONCAT PROCESSOR NAME
                processorName = f"{mName} {fName} {model}"
                PROCESSORS_OBJ[index] = {
                    "MANUFACTURER": mName,
                    "FAMILY": fName,
                    "MODEL": model,
                    "CLOCK_SPEED": cSpeed,
                    "CORE_COUNT": cCount,
                    "THREAD_COUNT": tCount
                    }

                print("PROCESSOR: {}".format(processorName))
                
            index += 1  
            print("=" * 100)

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(f"ERROR IN PROCESSOR FILE READ PROCESS: {E}")

# WRITE THE DATA TO FILE ==========================================================================
def step_3():
    with open(OUTPUT_FILE_NAME, mode="a+", encoding='utf-8') as f:
        f.write(str(json.dumps(PROCESSORS_OBJ, indent=4)))
        f.close()

#if __name__ == "__main__":
#    parser = ArgumentParser(description="Extract selected columns of data from CSV files.")
#    parser.add_argument("-i", type=str, help="CSV file name")
#    parser.add_argument("-o", type=str, help="Output file name.")
#
#    args = parser.parse_args()
#
#    if(len(sys.argv) < 2):
#        parser.print_help()
#        exit()
#
#    with open(args.i, encoding="UTF-8", mode="r") as f:
#        headings = f.readline()
#        print(headings, "\n")
#        f.close()
#
#    selected_columns = str(input("Enter Column Numbers to be extracted. EX: 0 3 4 9\n> ")).split(" ")

step_1()
step_2()
step_3()