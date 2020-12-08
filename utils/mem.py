import psutil

def getCPU(interval=1):

    return psutil.cpu_percent(interval)

def getMEM():
    pc_mem =psutil.virtual_memory()
    div_gb_factor = (1024.0 ** 3)

    return  float(pc_mem.free / div_gb_factor)


~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                                                                  
~                                                       
