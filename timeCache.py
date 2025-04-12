import time
from threading import Timer
import heapq
import LRUSet

# Might need to switch from timer to async in the future
"""
implements a cache with LRU replacement policy that autodeletes lines TTL
seconds after being added.
"""
class Cache:
    def __init__(self, maxSize=16, maxheap=None, LRUSize=16):
        # {(item, TTL): (expiry, data)}
        self._cache = {}
        # [expirationTime, (item, TTL)]
        self._expiration_heap = []
        #(item, TTL)
        self._lru = LRUSet.LRUSet(LRUSize)
        self._timer = None
        self.cacheSize = maxSize
        self.maxHeapSize = int(1.5 * maxSize) if not maxheap else maxheap
    
    """
    Prepares a timer for the top item in the expriration heap, the one
    that should be removed earlier.
    pre: _
    post: creates a timer for the first item in the expiration heap and
    removes any due cache entries
    returns: None
    """
    def _scheduleCleanup(self):
        if self._expiration_heap:
            key = self._expiration_heap[0][1]
            while (key not in self._cache or
                   self._expiration_heap[0][0] != self._cache[key][0]):
                heapq.heappop(self._expiration_heap)
                if not self._expiration_heap: return
                key = self._expiration_heap[0][1]
            
            soonestExp, key = self._expiration_heap[0]
            currentTime = time.time()
            TTL = soonestExp - currentTime
            if TTL > 0:
                self._timer = Timer(TTL, self._autoCleanup, args=[key])
                self._timer.start()
            else: self._autoCleanup(key)
    
    """
    if valid, removes the first heap entry and its correspondents
    pre: The heap eantry is valid, that is, its not a duplicate heap entry
    due to the lazy removal when applying LRU eviction policy
    post: Removes first element of the expiration heap and its correspondent
    cache and lru entry adn schedules the next timer
    returns: None
    """
    def _autoCleanup(self, key):
        if self._expiration_heap and self._expiration_heap[0][1] == key:
            self._cache.pop(key, None)
            heapq.heappop(self._expiration_heap)
            self._lru.discard(key)
            if self._expiration_heap: self._scheduleCleanup()
    
    """
    Cleans the expiration heap
    pre: _
    post: removes all duplicate (not valid) heap entries
    returns: None
    """
    def _cleanHeap(self):
        self._expiration_heap = [
            (exp, key) for (exp, key) in self._expiration_heap if key in self._cache
        ]
        heapq.heapify(self._expiration_heap)
    
    """
    Adds a new line to the cache
    pre: key (item, TTL) is not already present in the cache
    post: adds new line to the cache, if its full, removes one entry with
    lru eviction policy. If LRU is applied, the cache entry and lru entry from
    the evicted line are removed but for heap's entry lazy removing will be used
    returns: None
    """
    def addLine(self, item, data, TTL=60.0):
        if (item, TTL) in self._cache: return
        
        thisExp = time.time() + TTL
        
        self._cache[(item, TTL)] = (thisExp, data)
        heapq.heappush(self._expiration_heap, (thisExp, (item, TTL)))
        soonestExp, expKey = self._expiration_heap[0]
        
        self._lru.pushback((item, TTL))
        if len(self._cache) > self.cacheSize:
            lruKey = self._lru.popfront()
            self._cache.pop(lruKey, None)
            if lruKey == expKey:
                if self._timer:
                    self._timer.cancel()
                if len(self._expiration_heap) > self.maxHeapSize: self._cleanHeap()
                self._scheduleCleanup()
            
        if thisExp <= soonestExp:
            if self._timer: self._timer.cancel()
            self._scheduleCleanup()
    
    """
    Returns specified cache line
    pre: _
    post: updates LRU
    returns: None if not present, the tuple (expiration time, data) otherwise
    """
    def get(self, item, TTL):
        data = self._cache.get((item, TTL))
        if data:
            self._lru.pushback((item, TTL))
        return data
    
    def __contains__(self, key):
        return key in self._cache

    def __len__(self):
        return len(self._cache)
    
    #for testing
    def __str__(self):
        printStr = f'Cache(size={len(self._cache)}):\n******************\n'
        for key, value in self._cache.items():
            printStr += f'| {key} : {value} |\n'
        printStr += '******************\n'
        printStr += f'expiration Heap(size={len(self._expiration_heap)}):'
        printStr += '\n------------------\n'
        for item in self._expiration_heap:
            printStr += f'| {item} |\n'
        printStr += '------------------\n'
        printStr += f'LRU(size={len(self._lru)}):\n~~~~~~~~~~~~~~~~~~\n'
        printStr += str(self._lru)
        printStr += '~~~~~~~~~~~~~~~~~~\n'
        return printStr
        
    def _cleanCache(self):
        self._cache.clear()
        