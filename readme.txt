Properties Methods




getContentLanguage(self)
    Return the language of a resource's textual content or nu

    @return: string

getContentLength(self)
    Returns the length of the resource's content in bytes.

    @return: number of bytes

getContentType(self)
    Return the resource's content MIME type.

    @return: MIME type string

getCreationDate(self)
    Return date of creation as time tuple.

    @return: time tuple
    @rtype: C{time.struct_time}

    @raise ValueError: If string is not in the expected forma

getDisplayName(self)
    Returns a resource's display name.

    @return: string

getEntityTag(self)
    Return a entity tag which is unique for a particular vers
    Different resources or one resource before and after modi

    @return: entity tag string

getLastModified(self)
    Return last modification of resource as time tuple.

    @return: Modification date time.
    @rtype:  C{time.struct_time}

    @raise ValueError: If the date time string is not in the

getLockDiscovery(self)
    Return all current lock's applied to a resource or null i

    @return: a lockdiscovery DOM element according to RFC 281

getOwnerAsUrl(self)
    Return a resource's owner in form of a URL.

    @return: string

getResourceType(self)
    Return a resource's WebDAV type.

    @return: 'collection' or 'resource'

getSupportedLock(self)
    Return a DOM element describing all supported lock option
    Usually this is shared and exclusive write lock.

    @return: supportedlock DOM element according to RFC 2815


















Resource Methods






This class provides client access to a WebDAV collection resource identified by an URI.
This class does not cache resource data. This has to be performed by its clients.

@author: Roland Betz

Method resolution order:
    CollectionStorer
    ResourceStorer
    __builtin__.object

Methods defined here:

__init__(self, url, connection=None, validateResourceNames=True)
    Creates a CollectionStorer instance for a URL and an optional Connection object.
    User must invoke validate() after constuction to check the resource on the server.

    @see: L{webdav.WebdavClient.ResourceStorer.__init__}
    @param url: unique resource location for this storer
    @param connection: this optional parameter contains a Connection object for the host part
        of the given URL. Passing a connection saves memory by sharing this connection.

addCollection(self, name, lockToken=None)
    Make a new WebDAV collection resource within this collection.

    @param name: of the new collection
    @param lockToken: None or token returned by last lock operation
    @type  lockToken: L{LockToken}

addResource(self, name, content=None, properties=None, lockToken=None)
    Create a new empty WebDAV resource contained in this collection with the given
    properties.

    @param name: leaf name of the new resource
    @param content: None or initial binary content of resource
    @param properties: name/value-map containing properties
    @param lockToken: None or token returned by last lock operation
    @type  lockToken: L{LockToken}

deepFindProperties(self, *names)
    Retrieve given properties for this collection and all contained (nested) resources.

    Note:
    =====
      This operation can take a long time if used with recursive=true and is therefore
      disabled on some WebDAV servers.

    @param names: a list of property names
    @return: a map from resource URI to a map from property name to value.

deleteResource(self, name, lockToken=None)
    Delete a collection which is contained within this collection

    @param name: leaf name of a contained collection resource
    @param lockToken: None or token returned by last lock operation
    @type  lockToken: L{LockToken}

findAllProperties(self)
    Retrieve all properties for this collection and all directly contained resources.

    @return: a map from resource URI to a map from property name to value.

findProperties(self, *names)
    Retrieve given properties for this collection and all directly contained resources.

    @param names: a list of property names
    @return: a map from resource URI to a map from property name to value.

getCollectionContents(self)
    Return a list of the tuple (resources or collection) / properties)

    @return: a list of the tuple (resources or collection) / properties)
    @rtype: C{list}

getResourceStorer(self, name)
    Return a ResourceStorer instance for a child resource (member) of this Collection.

    @param name: leaf name of child resource
    @return: L{ResourceStorer} instance

listResources(self)
    Describe all members within this collection.

    @return: map from URI to a L{LiveProperties} instance containing the WebDAV
             live attributes of the contained resource

lockAll(self, owner)
    Locks this collection resource for exclusive write access. This means that for
    succeeding write operations the returned lock token has to be passed.
    The operation is applied recursively to all contained resources.
    If the methode does not throw an exception then the lock has been granted.

    @param owner: describes the lock holder
    @return: Lock token string (automatically generated).
    @rtype: L{LockToken}

search(self, conditions, selects)
    Search for contained resources which match the given search condition.

    @param conditions: tree of ConditionTerm instances representing a logical search term
    @param selects: list of property names to retrieve for the found resources

validate(self)
    Check whether this URL contains a WebDAV collection.
    Uses the WebDAV OPTION method.

    @raise WebdavError: L{WebdavError} if URL does not contain a WebDAV collection resource.

----------------------------------------------------------------------
Methods inherited from ResourceStorer:

__getattr__(self, name)
    Build-in method:
    Forwards unknow lookups (methods) to delegate object 'versionHandler'.

    @param name: name of unknown attribute

copy(self, toUrl, infinity=True)
    Copies this resource.

    @param toUrl: target URI path
    @param infinity: Flag that indicates that the complete content of collection is copied. (default)
    @type depth: C{boolean}

delete(self, lockToken=None)
    Deletes this resource.

    @param lockToken: String returned by last lock operation or null.
    @type  lockToken: L{LockToken}

deleteContent(self, lockToken=None)
    Delete binary data at permanent storage.

    @param lockToken: None or lock token from last lock request
    @type  lockToken: L{LockToken}

deleteProperties(self, lockToken=None, *names)
    Removes the given properties from this resource.

    @param lockToken: if the resource has been locked this is the lock token.
    @type  lockToken: L{LockToken}
    @param names: a collection of property names.
           A property name is a (XmlNameSpace, propertyName) tuple.

downloadContent(self, extra_hdrs={})
    Read binary data from permanent storage.

downloadFile(self, localFileName)
    Copy binary data from permanent storage to a local file.

    @param localFileName: file to write binary data to

getAcl(self)
    Returns this resource's ACL in an ACL instance.

    @return: Access Control List.
    @rtype: L{ACL<webdav.acp.Acl.ACL>}

getCurrentUserPrivileges(self)
    Returns a tuple of the current user privileges.

    @return: list of Privilege instances
    @rtype: list of L{Privilege<webdav.acp.Privilege.Privilege>}

getOwnerUrl(self)
    Explicitly retireve the Url of the owner.

getPrincipalCollections(self)
    Returns a list principal collection URLs.

    @return: list of principal collection URLs
    @rtype: C{list} of C{unicode} elements

getSpecificOption(self, option)
    Returns specified WebDav options.
    @param option: name of the option

    @return: String containing the value of the option.
    @rtype: C{string}

isConnectedToCatacombServer(self)
    Returns True if connected to a Catacomb WebDav server.

    @return: if connected to Catacomb Webdav server (True / False)
    @rtype: C{bool}

lock(self, owner)
    Locks this resource for exclusive write access. This means that for succeeding
    write operations the returned lock token has to be passed.
    If the methode does not throw an exception the lock has been granted.

    @param owner: describes the lock holder
    @return: lock token string (automatically generated)
    @rtype: L{LockToken}

move(self, toUrl)
    Moves this resource to the given path or renames it.

    @param toUrl: new (URI) path

options(self)
    Send an OPTIONS request to server and return all HTTP headers.

    @return: map of all HTTP headers returned by the OPTIONS method.

readAllProperties(self)
    Reads all properties of this resource.

    @return: a map from property names to DOM Element or String values.

readAllPropertyNames(self)
    Returns the names of all properties attached to this resource.

    @return: List of property names

readProperties(self, *names, **kwargs)
    Reads the given properties.

    @param names: a list of property names.
                  A property name is a (XmlNameSpace, propertyName) tuple.
    @param ignore404: a boolean flag.
                  Indicates if an error should be raised for missing properties.
    @return: a map from property names to DOM Element or String values.

readProperty(self, nameSpace, name)
    Reads the given property.

    @param nameSpace: XML-namespace
    @type nameSpace: string
    @param name: A property name.
    @type name: string

    @return: a map from property names to DOM Element or String values.

readStandardProperties(self)
    Read all WebDAV live properties.

    @return: A L{LiveProperties} instance which contains a getter method for each live property.

setAcl(self, acl, lockToken=None)
    Sets ACEs in the non-inherited and non-protected ACL or the resource.
    This is the implementation of the ACL method of the WebDAV ACP.

    @param acl: ACL to be set on resource as ACL object.
    @param lockToken: If the resource has been locked this is the lock token (defaults to None).
    @type  lockToken: L{LockToken}

unlock(self, lockToken)
    Removes the lock from this resource.

    @param lockToken: which has been return by the lock() methode
    @type  lockToken: L{LockToken}

uploadContent(self, content, lockToken=None, extra_hdrs={})
    Write binary data to permanent storage.

    @param content: containing binary data
    @param lockToken: None or lock token from last lock request
    @type  lockToken: L{LockToken}

uploadFile(self, newFile, lockToken=None)
    Write binary data to permanent storage.

    @param newFile: File containing binary data.
    @param lockToken: None or lock token from last lock request
    @type  lockToken: L{LockToken}

writeProperties(self, properties, lockToken=None)
    Sets or updates the given properties.

    @param lockToken: if the resource has been locked this is the lock token.
    @type  lockToken: L{LockToken}
    @param properties: a map from property names to a String or
                       DOM element value for each property to add or update.

----------------------------------------------------------------------
Data descriptors inherited from ResourceStorer:

__dict__
    dictionary for instance variables (if defined)

__weakref__
    list of weak references to the object (if defined)

aclSupportAvailable
    Returns True if the current connection has got ACL support.

    @return: ACL support (True / False)
    @rtype: C{bool}

daslBasicsearchSupportAvailable
    Returns True if the current connection supports DASL basic search.

    @return: DASL basic search support (True / False)
    @rtype: C{bool}

url
    Resource's URL