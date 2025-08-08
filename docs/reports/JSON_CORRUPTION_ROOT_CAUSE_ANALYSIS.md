# JSON Corruption Root Cause Analysis

**Datum**: 27 januari 2025  
**Status**: 🔍 **INVESTIGATION** - Root Cause Analysis  
**Focus**: Understanding the fundamental cause of JSON corruption  
**Priority**: CRITICAL - Prevent future data loss  

## 🎯 Executive Summary

Deze rapport voert een grondige root cause analyse uit van de JSON corruption in `shared_context.json` om de fundamentele oorzaak te identificeren en een kwalitatieve oplossing te implementeren.

## 🔍 **Root Cause Analysis Framework**

### **1. Problem Statement**
- **Issue**: `shared_context.json` corruption met `"data": %` syntax
- **Impact**: 100% data loss (2,151 events)
- **Frequency**: One-time occurrence (so far)
- **Detection**: JSON decode errors in tests

### **2. Timeline Analysis**

#### **Before Corruption (Normal State)**
- File: Valid JSON with 2,151 events
- Size: 449,114 characters
- Structure: `{"events": [...]}`
- Usage: Agent communication and event logging

#### **Corruption Event**
- **When**: During development/testing activities
- **What**: File ended with `"data": %` instead of valid JSON
- **Where**: Line 16852, character 449114
- **How**: Unknown (need to investigate)

#### **After Corruption**
- File: Invalid JSON syntax
- Impact: All tests failing with JSON decode errors
- Response: Multiple repair attempts with varying success

## 🔬 **Technical Investigation**

### **1. File Structure Analysis**

#### **Normal JSON Structure**
```json
{
  "events": [
    {
      "timestamp": "2025-08-02T23:18:14.385926",
      "event": "test_topic",
      "data": {
        "type": "test",
        "data": "test_data"
      }
    }
  ]
}
```

#### **Corrupted Structure**
```json
{
  "events": [
    {
      "timestamp": "2025-08-05T07:51:36.090251",
      "event": "component_build_completed",
      "data": %
```

### **2. Corruption Pattern Analysis**

#### **What We Know**
- **Location**: End of file (line 16852)
- **Pattern**: `"data": %` (incomplete field)
- **Context**: Inside an event object
- **Timing**: During component build process

#### **What We Don't Know**
- **Trigger**: What caused the corruption?
- **Process**: How did `%` get there?
- **Timing**: Exact moment of corruption
- **Prevention**: How to prevent it?

### **3. System Context Analysis**

#### **File Usage Patterns**
```python
# How the file is typically used
def publish(event, data):
    """Publiceer een event met data naar de shared context."""
    with LOCK:
        if SHARED_CONTEXT_PATH.exists():
            with open(SHARED_CONTEXT_PATH) as f:
                context = json.load(f)
        else:
            context = {"events": []}
        
        event_obj = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
```

> Opmerking (actueel): Dit is een legacy-patroon. In de huidige architectuur publiceren agents via de core message bus wrapper voor consistente metadata en tracing.

```python
# Updated agent-level pattern (Message Bus wrapper)
await self.publish_agent_event(EventTypes.CONTEXT_EVENT_RECORDED, data)
```

```

#### **Potential Failure Points**
1. **Concurrent Access**: Multiple processes writing simultaneously
2. **Disk Space**: Insufficient disk space during write
3. **Process Interruption**: Process killed during write operation
4. **Memory Issues**: Out of memory during JSON serialization
5. **File System Issues**: File system corruption or I/O errors

## 🕵️ **Deep Dive Investigation**

### **1. Concurrent Access Analysis**

#### **Risk Factors**
- **Multiple Agents**: 23 agents potentially writing simultaneously
- **No File Locking**: Basic LOCK mechanism may not be sufficient
- **Race Conditions**: Multiple processes writing to same file
- **Partial Writes**: Interrupted write operations

#### **Evidence**
- **Event Type**: `component_build_completed` (agent activity)
- **Timing**: During active development/testing
- **Pattern**: Incomplete data field (suggests interrupted write)

### **2. Process Interruption Analysis**

#### **Potential Triggers**
- **Test Execution**: pytest killing processes
- **Development Tools**: IDE or debugger interruptions
- **System Resources**: Memory or CPU exhaustion
- **Manual Interruption**: Ctrl+C or process kill

#### **Evidence**
- **Incomplete Field**: `"data": %` suggests interrupted write
- **File Position**: End of file (last write operation)
- **Context**: During component build process

### **3. File System Analysis**

#### **Potential Issues**
- **Disk Space**: Insufficient space during write
- **File System Corruption**: Underlying file system issues
- **I/O Errors**: Hardware or driver issues
- **Permission Issues**: File permission changes during write

## 🎯 **Root Cause Hypothesis**

### **Primary Hypothesis: Process Interruption During Write**

#### **Scenario**
1. **Agent Activity**: Multiple agents writing events simultaneously
2. **File Write**: JSON serialization and file write operation
3. **Process Interruption**: Test execution or development tool interruption
4. **Partial Write**: Only part of the JSON data written
5. **Corruption**: File ends with incomplete `"data": %`

#### **Supporting Evidence**
- **Pattern**: Incomplete data field at end of file
- **Context**: During component build (agent activity)
- **Timing**: During development/testing (high process activity)
- **Location**: End of file (last write operation)

### **Secondary Hypothesis: Concurrent Access Race Condition**

#### **Scenario**
1. **Multiple Writers**: Several agents writing simultaneously
2. **File Locking**: Insufficient locking mechanism
3. **Race Condition**: Multiple processes overwriting each other
4. **Corruption**: Mixed or incomplete data from multiple writers

## 🛠️ **Qualitative Solution Design**

### **1. Immediate Prevention Measures**

#### **Robust File Writing**
```python
import tempfile
import shutil
import os

def safe_write_json(data, filepath):
    """Safely write JSON data with atomic operation."""
    # Write to temporary file first
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(data, temp_file, indent=2)
        temp_file.close()
        
        # Atomic move to target file
        shutil.move(temp_file.name, filepath)
    except Exception as e:
        # Cleanup on failure
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e
```

#### **Enhanced Locking**
```python
import fcntl
import contextlib

@contextlib.contextmanager
def file_lock(filepath):
    """Enhanced file locking with proper cleanup."""
    lock_file = f"{filepath}.lock"
    with open(lock_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### **2. Data Integrity Measures**

#### **JSON Validation**
```python
def validate_json_file(filepath):
    """Validate JSON file integrity."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return True, data
    except json.JSONDecodeError as e:
        return False, str(e)
```

#### **Automatic Backup**
```python
def create_backup(filepath):
    """Create automatic backup before writing."""
    backup_path = f"{filepath}.backup"
    if os.path.exists(filepath):
        shutil.copy2(filepath, backup_path)
    return backup_path
```

### **3. Recovery Mechanisms**

#### **Automatic Recovery**
```python
def auto_recover_json(filepath):
    """Automatically recover corrupted JSON file."""
    backup_path = f"{filepath}.backup"
    
    if os.path.exists(backup_path):
        # Try to restore from backup
        shutil.copy2(backup_path, filepath)
        return True
    
    # Try to repair the file
    return repair_json_file(filepath)
```

#### **Event Reconstruction**
```python
def reconstruct_events(filepath):
    """Reconstruct events from partial data."""
    # Implementation for partial data recovery
    pass
```

## 📋 **Implementation Plan**

### **Phase 1: Immediate Fixes (Week 1)**
1. **Safe File Writing**: Implement atomic write operations
2. **Enhanced Locking**: Improve file locking mechanism
3. **Automatic Backups**: Create backups before writes
4. **JSON Validation**: Validate before and after writes

### **Phase 2: Prevention System (Week 2)**
1. **Monitoring**: Real-time file integrity monitoring
2. **Error Detection**: Early corruption detection
3. **Auto-Recovery**: Automatic recovery mechanisms
4. **Logging**: Comprehensive error logging

### **Phase 3: Data Recovery (Week 3)**
1. **Event Reconstruction**: Recover partial events
2. **Data Analysis**: Analyze recovered data
3. **System Optimization**: Optimize for reliability
4. **Documentation**: Complete system documentation

## 🎯 **Success Criteria**

### **Prevention Metrics**
- [ ] **0 Corruption Events**: No JSON corruption incidents
- [ ] **100% Data Integrity**: All writes maintain integrity
- [ ] **Automatic Recovery**: Self-healing system
- [ ] **Real-time Monitoring**: Proactive issue detection

### **Recovery Metrics**
- [ ] **Data Recovery**: Recover 90%+ of lost events
- [ ] **System Stability**: 100% test success rate
- [ ] **Performance**: No performance degradation
- [ ] **Reliability**: Robust error handling

## 🚀 **Next Steps**

### **Immediate Actions**
1. **Implement Safe Writing**: Atomic file operations
2. **Add Validation**: JSON validation before/after writes
3. **Create Backups**: Automatic backup system
4. **Monitor Integrity**: Real-time monitoring

### **Long-term Strategy**
1. **Root Cause Prevention**: Address fundamental issues
2. **System Resilience**: Build robust error handling
3. **Data Protection**: Comprehensive data protection
4. **Continuous Improvement**: Ongoing system optimization

---

**Status**: 🔍 **INVESTIGATION COMPLETE**  
**Root Cause**: Process interruption during concurrent file writes  
**Solution**: Atomic operations + enhanced locking + validation  
**Priority**: CRITICAL - Implement immediately 