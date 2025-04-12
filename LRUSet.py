"""
Implements a Set taht places new items to the back leaving the old ones at
the front. O(n) time complexity for print and iteration O(1) for the rest
"""
##add max len handling
class LRUSet:
    def __init__(self, LRUsize=16):
        # maps keys to their respective nodes
        self._key2node = {}
        self._head = self._tail = None
        self._maxSize = LRUsize

    class _Node:
        def __init__(self, key):
            self.key = key
            self.prev = self.next = None
            
    """
    remove node, if its not present it wont throw any error
    pre: _
    post: if present, removes node with key from LRU
    return: None
    """
    def discard(self, key):
        node = self._key2node.pop(key, None)
        if not node: return
        
        if node.prev: node.prev.next = node.next
        else: self._head = node.next
        
        if node.next: node.next.prev = node.prev
        else: self._tail = node.prev
    
    """
    remove first element of the LRU, the one that was added the longest ago
    pre: lru not empty
    post: if lru not empty removes first element
    return: key of the removed node
    """
    def popfront(self):
        if not self._head:
            raise KeyError("pop in empty LRU")
        key = self._head.key
        self.discard(key)
        return key
    
    """
    adds node wit key to the back, if present it moves it to the back
    pre: _
    post: if present, removes node with key from LRU
    return: None
    """
    def pushback(self, key):
        # move present node to the end
        if key in self._key2node:
            node = self._key2node[key]
            
            if node is self._tail: return
            
            if node.prev: node.prev.next = node.next
            else: self._head = node.next
            
            if node.next: node.next.prev = node.prev
            else: self._tail = node.prev
            
            node.prev = self._tail
            node.next = None
            
            if self._tail: self._tail.next = node
            self._tail = node
            
            if not self._head: self._head = node
            return
        
        #add new node to the end
        node = self._Node(key)
        self._key2node[key] = node
        
        if self._tail:
            self._tail.next = node
            node.prev = self._tail
            self._tail = node
        else:
            self._head = self._tail = node
        
        #if LRU is full remove longest unused node
        if len(self._key2node) > self._maxSize: self.popfront()
    
    def __contains__(self, key):
        return key in self._key2node

    def __len__(self):
        return len(self._key2node)
    
    def __iter__(self):
        node = self._head
        while node:
            yield node.key
            node = node.next
            
    def __str__(self):
        elements = []
        node = self._head
        while node:
            elements.append(str(node.key))
            node = node.next
        return "LRU[" + " -> ".join(elements) + "]\n"
    