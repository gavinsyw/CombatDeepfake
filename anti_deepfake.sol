pragma solidity ^0.6.6;

contract Anti_Deepfake {
    
    address public owner;
    // the video offline on the IPFS
    Video public thisVideo;
    // authorization license for the video
    bytes32 public license;
    
    struct Video {
        address owner;
        string info;            // additional information about the video
        bytes32 IPFS_hash;      // the hash of the video on IPFS
        bytes32 contract_address;
        string metadata;        
        uint256 timestamp;
    }
    
    enum artistState {SentRequest, GrantedPermission, DeniedPermission, SentAttestationRequest, GrantedAttestation, DeniedAttestation}
    
    struct Artist {
        artistState state;
        address EA;
        bytes32 hash;
        bool result;
    }
    
    bool parent;
    Video public parent_video;
    bytes32 private recent_video;
    address private recent_artist;
    
    mapping (bytes32 => Video) public Granted_Permission_ChildVideos;
    mapping (bytes32 => Artist) public Granted_Permissions;
    mapping (bytes32 => Artist) public Denied_Permissions;
    mapping (address => bool) public Not_Trusted_Artist;
    mapping (bytes32 => Artist) public Requests;
    
    modifier IsOwner() {
        require(msg.sender == owner);
        _;
    }
    
    modifier NotOwner() {
        require(msg.sender != owner);
        _;
    }
    
    event ArtistRequestingPermission(address artist);
    event ArtistRequestRegistered(address artist, bytes32 IPFS_hash);
    event PermissionGranted(string info, address artist);
    event PermissionDenied(string info, address artist);
    event AttestationRequest(string info, bytes32 contract_address);
    event AttestationGranted(string info, bytes32 contract_address);
    event AttestationDenied(string info, bytes32 contract_address);
    event ArtistRequestingRecheck(address artist);
    event RecheckGranted(string info, address artist);
    event RecheckDenied(string info, address artist);
    
    
    constructor(string memory info, bytes32 hash, string memory metadata, bytes32 license_addr) public {
        owner = msg.sender;
        parent = false;
        thisVideo.owner = msg.sender;
        thisVideo.IPFS_hash = hash;
        thisVideo.info = info;
        thisVideo.metadata = metadata;
        thisVideo.timestamp = block.timestamp;
        license = license_addr;
        recent_artist = msg.sender;
    }
    
    function updateProvenanceData(string memory info, bytes32 hash, string memory metadata, bytes32 contract_addr, address owner_addr) IsOwner public {
        parent = true;
        parent_video.owner = owner_addr;
        parent_video.info = info;
        parent_video.IPFS_hash = hash;
        parent_video.metadata = metadata;
        parent_video.contract_address = contract_addr;
        parent_video.owner = owner_addr;
    }
    
    function requestPermission(bool antideepfake_result, bytes32 IPFS_hash) NotOwner public {
        address artist = msg.sender;
        emit ArtistRequestingPermission(address(msg.sender));
        if (antideepfake_result && !Not_Trusted_Artist[msg.sender]) {
            Granted_Permissions[IPFS_hash].EA     = artist;
            Granted_Permissions[IPFS_hash].state  = artistState.GrantedPermission;
            Granted_Permissions[IPFS_hash].result = antideepfake_result;
            Granted_Permissions[IPFS_hash].hash   = IPFS_hash;
            recent_artist = msg.sender;
            PermissionGranted("Permission Granted to artist with address ", address(msg.sender));
        } 
        else if (Not_Trusted_Artist[msg.sender]) {
            PermissionDenied("Permission Denied to artist with address ", address(msg.sender));
        }
        else {
            Denied_Permissions[recent_video].state  = artistState.DeniedPermission;
            Denied_Permissions[recent_video].result = false;
            Denied_Permissions[recent_video].hash   = recent_video;
            Not_Trusted_Artist[recent_artist]  = true;
            // default: deepfake for original owner is true
            Granted_Permissions[IPFS_hash].EA     = artist;
            Granted_Permissions[IPFS_hash].state  = artistState.GrantedPermission;
            Granted_Permissions[IPFS_hash].result = antideepfake_result;
            Granted_Permissions[IPFS_hash].hash   = IPFS_hash;
            PermissionGranted("Permission Granted to artist with address ", address(msg.sender));
        }
        emit ArtistRequestRegistered(address(msg.sender), IPFS_hash);
    }
    
    function requestRecheck(bytes32 IPFS_hash) NotOwner public {
        require(Requests[IPFS_hash].hash != IPFS_hash);
        emit ArtistRequestingRecheck(address(msg.sender));
        Requests[IPFS_hash].state = artistState.SentRequest;
        Requests[IPFS_hash].EA = msg.sender;
        Requests[IPFS_hash].hash = IPFS_hash;
        Requests[IPFS_hash].result = false;
        emit ArtistRequestRegistered(address(msg.sender), IPFS_hash);
    }
    
    function grantRecheckPermission(bool result, address artist, bytes32 IPFS_hash) IsOwner public {
        require(Requests[IPFS_hash].state == artistState.SentRequest);
        if (result) {
            Granted_Permissions[IPFS_hash].EA = artist;
            Granted_Permissions[IPFS_hash].state = artistState.GrantedPermission;
            Granted_Permissions[IPFS_hash].result = result;
            Granted_Permissions[IPFS_hash].hash = IPFS_hash;
            Requests[IPFS_hash].state = artistState.GrantedPermission;
            Requests[IPFS_hash].result = true;
            Not_Trusted_Artist[artist] = false;
            PermissionGranted("Permission Granted to artist with address ", address(artist));
        }
        else {
            Denied_Permissions[IPFS_hash].EA = artist;
            Denied_Permissions[IPFS_hash].state = artistState.DeniedPermission;
            Denied_Permissions[IPFS_hash].result = result;
            Denied_Permissions[IPFS_hash].hash = IPFS_hash;
            Requests[IPFS_hash].state == artistState.DeniedPermission;
            PermissionDenied("Permission Denied to address ", artist);
        }
    }
    
    function requestDenyPermission(address artist, bytes32 IPFS_hash, bool untrusted) IsOwner public {
        Denied_Permissions[IPFS_hash].EA = artist;
        Denied_Permissions[IPFS_hash].state = artistState.DeniedPermission;
        Denied_Permissions[IPFS_hash].result = false;
        Denied_Permissions[IPFS_hash].hash = IPFS_hash;
        PermissionDenied("Permission Denied to address ", artist);
        Not_Trusted_Artist[artist] = untrusted;
    }
    
    //this function is called by the artist after getting an approval and creating a child SC 
    function AttestSC(bytes32 hash, bytes32 contract_addr) NotOwner public{
        require(Granted_Permissions[hash].state == artistState.GrantedPermission);//requires state to be granted
        AttestationRequest("Address of child: " , contract_addr);
        Granted_Permissions[hash].state = artistState.SentAttestationRequest;
    }
    
    function GrantAttestation(bool result, string memory infor, bytes32 hash, string memory meta, bytes32 contract_addr) IsOwner public{
    require(Granted_Permissions[hash].state == artistState.SentAttestationRequest);
        if(result){
         Granted_Permission_ChildVideos[hash].owner = msg.sender;//save all info as new entry
         Granted_Permission_ChildVideos[hash].info = infor;
         Granted_Permission_ChildVideos[hash].IPFS_hash = hash;
         Granted_Permission_ChildVideos[hash].contract_address = contract_addr;
         Granted_Permission_ChildVideos[hash].timestamp = block.timestamp;
         Granted_Permission_ChildVideos[hash].metadata = meta;
         Granted_Permissions[hash].state = artistState.GrantedAttestation;
         AttestationGranted("Successfully Attested: ", contract_addr);
        }
        else
        {
         Granted_Permissions[hash].state = artistState.DeniedAttestation;//Granted permission for the request, but denied attestation
         AttestationDenied("Denied Attestation: ", contract_addr);   
        }
    }
    
}