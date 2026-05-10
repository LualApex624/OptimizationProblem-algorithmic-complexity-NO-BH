CXX = g++
CXXFLAGS = -std=c++17 -O3 -march=native -DNDEBUG
CXXFLAGS_DEBUG = -std=c++17 -g -O0 -fsanitize=address

TARGET = transport
SRC = transport.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

debug: $(SRC)
	$(CXX) $(CXXFLAGS_DEBUG) -o $(TARGET)_debug $<

clean:
	rm -f $(TARGET) $(TARGET)_debug benchmark_cpp.csv

.PHONY: all debug clean
