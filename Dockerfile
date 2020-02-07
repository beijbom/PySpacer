FROM nvidia/cuda:8.0-cudnn6-devel-ubuntu16.04
LABEL maintainer maplerme@gmail.com

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        python3-dev \
        python-numpy \
        python3-pip \
        python3-setuptools \
        python-scipy && \
    rm -rf /var/lib/apt/lists/*

ENV CAFFE_ROOT=/opt/caffe
WORKDIR $CAFFE_ROOT

# FIXME: use ARG instead of ENV once DockerHub supports this
# https://github.com/docker/hub-feedback/issues/460
ENV CLONE_TAG=1.0

RUN git clone -b ${CLONE_TAG} --depth 1 https://github.com/BVLC/caffe.git . && \
    cd python && for req in $(cat requirements.txt) pydot 'python-dateutil>2'; do pip3 install $req; done && cd .. && \
    mkdir build && cd build && \
    cmake -DCPU_ONLY=1 -Dpython_version=3 .. && \
    make -j"$(nproc)"

ENV PYCAFFE_ROOT $CAFFE_ROOT/python
ENV PYTHONPATH $PYCAFFE_ROOT:$PYTHONPATH
ENV PATH $CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH
RUN echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig

WORKDIR /workspace

# Note, the proper way to use the mapler dockerfile would be to inherit FROM that definition.
# But when trying that it was compiled with CUDA, so it gave me trouble.
# Start spacer Custom comments

RUN apt-get update
RUN apt-get install vim -y

LABEL maintainer oscar.beijbom@gmail.com

RUN pip3 install --upgrade pip

RUN pip3 install boto
RUN pip3 install wget
RUN pip3 install scikit-learn==0.17.1
RUN pip3 install scikit-image
RUN pip3 install scipy==0.19.1
RUN pip3 install numpy==1.17.0

WORKDIR /root/.aws
COPY secrets credentials

WORKDIR /workspace
COPY . spacer
RUN PYTHONPATH=$PYTHONPATH:/workspace/spacer
RUN mkdir models


WORKDIR spacer
# RUN pip3 install -r requirements.txt
CMD python3 -m unittest