# Compilation notes for GPU

## OneDNN with AMD ROCM based GPU


https://codeplay.com/portal/blogs/2022/12/16/bringing-nvidia-and-amd-support-to-oneapi.html
https://developer.codeplay.com/products/oneapi/amd/2023.0.0/guides/get-started-guide-amd


```
# . intel/oneapi/setvars.sh
# sycl-ls
[opencl:acc:0] Intel(R) FPGA Emulation Platform for OpenCL(TM), Intel(R) FPGA Emulation Device 1.2 [2022.15.12.0.01_081451]
[opencl:cpu:1] Intel(R) OpenCL, Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz 3.0 [2022.15.12.0.01_081451]
[ext_oneapi_hip:gpu:0] AMD HIP BACKEND, Device 6861 0.0 [HIP 327.50]
```



```bash
wget -q https://github.com/oneapi-src/oneDNN/archive/refs/tags/v3.0.tar.gz
tar xf v3.0.tar.gz
rm *.tar.gz
cd oneDNN-*
export CPPFLAGS='-I/opt/rocm/miopen/include -I/opt/rocm/hip/include -I/opt/rocm/rocblas/include'
export LD_LIBRARY_PATH='-L/opt/rocm/miopen/lib'
cmake -DCMAKE_BUILD_TYPE=Release -DDNNL_LIBRARY_TYPE=SHARED -DDNNL_GPU_RUNTIME=OCL -DDNNL_BUILD_EXAMPLES=OFF -DDNNL_BUILD_TESTS=OFF -DDNNL_ENABLE_WORKLOAD=INFERENCE -DDNNL_ENABLE_PRIMITIVE="CONVOLUTION;REORDER" -DDNNL_GPU_VENDOR=AMD -DCMAKE_INSTALL_PREFIX=/home/santhosh/lib .

make -j$(nproc) install
cd ..
rm -r oneDNN-*
```

One DNN Compilation log

```
-- The C compiler identification is Clang 16.0.0
-- The CXX compiler identification is Clang 16.0.0
-- Check for working C compiler: /home/santhosh/intel/oneapi/compiler/2023.0.0/linux/bin/icx
-- Check for working C compiler: /home/santhosh/intel/oneapi/compiler/2023.0.0/linux/bin/icx -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /home/santhosh/intel/oneapi/compiler/2023.0.0/linux/bin/icpx
-- Check for working CXX compiler: /home/santhosh/intel/oneapi/compiler/2023.0.0/linux/bin/icpx -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- DNNL_TARGET_ARCH: X64
-- DNNL_LIBRARY_NAME: dnnl
-- Performing Test SYCL_FLAG_SUPPORTED
-- Performing Test SYCL_FLAG_SUPPORTED - Success
-- Looking for pthread.h
-- Looking for pthread.h - found
-- Looking for pthread_create
-- Looking for pthread_create - not found
-- Looking for pthread_create in pthreads
-- Looking for pthread_create in pthreads - not found
-- Looking for pthread_create in pthread
-- Looking for pthread_create in pthread - found
-- Found Threads: TRUE
-- Found HIP: /opt/rocm-4.2.0/lib/libamdhip64.so (found version "4.2.21155")
-- Found rocBLAS: /opt/rocm-4.2.0/lib/librocblas.so (found version "2.38.0")
-- Found MIOpen: /opt/rocm-4.2.0/lib/libMIOpen.so (found version "2.11.0")
-- Found OpenMP_C: -fopenmp=libiomp5
-- Found OpenMP_CXX: -fopenmp=libiomp5
-- Found OpenMP: TRUE
-- Could NOT find Doxygen (missing: DOXYGEN_EXECUTABLE)
-- Could NOT find Doxyrest (missing: DOXYREST_EXECUTABLE)
-- Found PythonInterp: /usr/bin/python2.7 (found suitable version "2.7.16", minimum required is "2.7")
-- Found Sphinx: /usr/bin/sphinx-build (found version "sphinx-build 1.8.4")
-- Found Git: /usr/bin/git (found version "2.20.1")
fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
-- Enabled workload: INFERENCE
-- Enabled primitives: CONVOLUTION;REORDER
-- Enabled primitive CPU ISA: ALL
-- Enabled primitive GPU ISA: ALL
-- Primitive cache is enabled
-- The ASM compiler identification is unknown
-- Found assembler: /home/santhosh/intel/oneapi/compiler/2023.0.0/linux/bin/icx
-- Warning: Did not find file Compiler/-ASM
-- Configuring done
-- Generating done
-- Build files have been written to: /home/santhosh/oneDNN-3.0/build
```

Patch:

https://github.com/intel/llvm/issues/7223



### CTranslate2 with GPU

```bash
wget https://github.com/OpenNMT/CTranslate2/archive/refs/tags/v3.3.0.tar.gz
tar xf *.tar.gz
rm *.tar.gz
cd CTranslate2-*
mkdir build && cd build
cmake -DWITH_DNNL=ON -DWITH_MKL=OFF -DOPENMP_RUNTIME=COMP -DCMAKE_BUILD_TYPE=Release  -DCMAKE_PREFIX_PATH=/home/santhosh/lib ..
VERBOSE=1 make -j$(nproc) install
cd ..
cd python
pip install -r install_requirements.txt
export CPPFLAGS='-I/home/santhosh/lib/include'
export LDFLAGS='-L/home/santhosh/lib/lib'
export LD_LIBRARY_PATH=/home/santhosh/lib/lib
python setup.py bdist_wheel
pip install dist/*.whl
```

In a virtual environment,

```
pip install -r requirements.txt
gunicorn
```

And open 0.0.0.0:8088 using your web browser.
