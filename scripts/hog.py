import sys, multiprocessing as mp
def work():
    SZ=256*1024*1024               # 256 MB >> LLC -> streams from DRAM
    src=bytearray(SZ); dst=bytearray(SZ)
    i=0
    while True:
        dst[:]=src                 # ~memmove of 256MB per iter (C speed)
        i=(i+1)&0xff; src[i]=i     # touch to avoid any optimisation
def main():
    n=int(sys.argv[1]) if len(sys.argv)>1 else 4
    ps=[mp.Process(target=work) for _ in range(n)]
    for p in ps: p.start()
    for p in ps: p.join()
if __name__=="__main__": main()
