// https://github.com/tonylukasavage/jsstl/blob/master/index.html

var camera, controls, scene, renderer,
geometry, material, mesh, light1, stats, stlEl;

function trim (str) {
    str = str.replace(/^\s+/, '');
    for (var i = str.length - 1; i >= 0; i--) {
        if (/\S/.test(str.charAt(i))) {
            str = str.substring(0, i + 1);
            break;
        }
    }
    return str;
}
// Notes:
// - STL file format: http://en.wikipedia.org/wiki/STL_(file_format)
// - 80 byte unused header
// - All binary STLs are assumed to be little endian, as per wiki doc
var parseStlBinary = function(stl) {
    var geo = new THREE.Geometry();
    var dv = new DataView(stl, 80); // 80 == unused header
    var isLittleEndian = true;
    var triangles = dv.getUint32(0, isLittleEndian); 
    var offset = 4;
    for (var i = 0; i < triangles; i++) {
        // Get the normal for this triangle
        var normal = new THREE.Vector3(
            dv.getFloat32(offset, isLittleEndian),
            dv.getFloat32(offset+4, isLittleEndian),
            dv.getFloat32(offset+8, isLittleEndian)
        );
        offset += 12;
        // Get all 3 vertices for this triangle
        for (var j = 0; j < 3; j++) {
            geo.vertices.push(
                new THREE.Vector3(
                    dv.getFloat32(offset, isLittleEndian),
                    dv.getFloat32(offset+4, isLittleEndian),
                    dv.getFloat32(offset+8, isLittleEndian)
                )
            );
            offset += 12
        }
        // there's also a Uint16 "attribute byte count" that we
        // don't need, it should always be zero.
        offset += 2;   
        // Create a new face for from the vertices and the normal             
        geo.faces.push(new THREE.Face3(i*3, i*3+1, i*3+2, normal));
    }
    // The binary STL I'm testing with seems to have all
    // zeroes for the normals, unlike its ASCII counterpart.
    // We can use three.js to compute the normals for us, though,
    // once we've assembled our geometry. This is a relatively 
    // expensive operation, but only needs to be done once.
    geo.computeFaceNormals();
    mesh = new THREE.Mesh( 
        geo,
        // new THREE.MeshNormalMaterial({
        //     overdraw:true
        // }
        new THREE.MeshLambertMaterial({
            overdraw:true,
            color: 0xaa0000,
            shading: THREE.FlatShading
        }
    ));
    scene.add(mesh);
    stl = null;
};  
var parseStl = function(stl) {
    var state = '';
    var lines = stl.split('\n');
    var geo = new THREE.Geometry();
    var name, parts, line, normal, done, vertices = [];
    var vCount = 0;
    stl = null;
    for (var len = lines.length, i = 0; i < len; i++) {
        if (done) {
            break;
        }
        line = trim(lines[i]);
        parts = line.split(' ');
        switch (state) {
            case '':
                if (parts[0] !== 'solid') {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "solid"');
                    return;
                } else {
                    name = parts[1];
                    state = 'solid';
                }
                break;
            case 'solid':
                if (parts[0] !== 'facet' || parts[1] !== 'normal') {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "facet normal"');
                    return;
                } else {
                    normal = [
                        parseFloat(parts[2]), 
                        parseFloat(parts[3]), 
                        parseFloat(parts[4])
                    ];
                    state = 'facet normal';
                }
                break;
            case 'facet normal':
                if (parts[0] !== 'outer' || parts[1] !== 'loop') {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "outer loop"');
                    return;
                } else {
                    state = 'vertex';
                }
                break;
            case 'vertex': 
                if (parts[0] === 'vertex') {
                    geo.vertices.push(new THREE.Vector3(
                        parseFloat(parts[1]),
                        parseFloat(parts[2]),
                        parseFloat(parts[3])
                    ));
                } else if (parts[0] === 'endloop') {
                    geo.faces.push( new THREE.Face3( vCount*3, vCount*3+1, vCount*3+2, new THREE.Vector3(normal[0], normal[1], normal[2]) ) );
                    vCount++;
                    state = 'endloop';
                } else {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "vertex" or "endloop"');
                    return;
                }
                break;
            case 'endloop':
                if (parts[0] !== 'endfacet') {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "endfacet"');
                    return;
                } else {
                    state = 'endfacet';
                }
                break;
            case 'endfacet':
                if (parts[0] === 'endsolid') {
                    //mesh = new THREE.Mesh( geo, new THREE.MeshNormalMaterial({overdraw:true}));
                    mesh = new THREE.Mesh( 
                        geo, 
                        new THREE.MeshLambertMaterial({
                            overdraw:true,
                            color: 0xaa0000,
                            shading: THREE.FlatShading
                        }
                    ));
                    scene.add(mesh);
                    done = true;
                } else if (parts[0] === 'facet' && parts[1] === 'normal') {
                    normal = [
                        parseFloat(parts[2]), 
                        parseFloat(parts[3]), 
                        parseFloat(parts[4])
                    ];
                    state = 'facet normal';
                } else {
                    console.error(line);
                    console.error('Invalid state "' + parts[0] + '", should be "endsolid" or "facet normal"');
                    return;
                }
                break;
            default:
                console.error('Invalid state "' + state + '"');
                break;
        }
    }
};

function resizeSTL(){
    camera.aspect = $(stlEl).width() / $(stlEl).height();
    camera.updateProjectionMatrix();
    renderer.setSize( $(stlEl).width(), $(stlEl).height());
    render();
}

function init(stl, el) {
    stlEl = el;
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 75, $(el).width() / $(el).height(), 1, 10000 );
    camera.position.z = 70;
    camera.position.y = 0;
    
    controls = new THREE.TrackballControls( camera );
	controls.rotateSpeed = 5.0;
	controls.zoomSpeed = 0.5;
    controls.minDistance = 1;
    controls.maxDistance = 1000;
	controls.panSpeed = 1.0;
	controls.noZoom = false;
	controls.noPan = false;
	controls.staticMoving = false;
	controls.dynamicDampingFactor = 0.3;
	controls.keys = [ 65, 83, 68 ];
	controls.addEventListener( 'change', render );
	
	window.addEventListener('resize', resizeSTL, false );
    
    scene.add( camera );
    
    var directionalLight1 = new THREE.DirectionalLight( 0xaaaaaa );
    directionalLight1.position.x = 0; 
    directionalLight1.position.y = 0; 
    directionalLight1.position.z = 1; 
    directionalLight1.position.normalize();
    
    var directionalLight2 = new THREE.DirectionalLight( 0xaaaaaa );
    directionalLight2.position.x = 0; 
    directionalLight2.position.y = 0; 
    directionalLight2.position.z = -1; 
    directionalLight2.position.normalize();
    
    ambientlight = new THREE.AmbientLight( 0x222222 );
				
    scene.add( ambientlight );
    scene.add( directionalLight1 );
    scene.add( directionalLight2 );
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if ( xhr.readyState == 4 ) {
            if ( xhr.status == 200 || xhr.status == 0 ) {
                var rep = xhr.response; // || xhr.mozResponseArrayBuffer;
                //parseStlBinary(rep);
                parseStl(xhr.responseText);
                mesh.rotation.x = 5;
                mesh.rotation.z = .25;
                render();
            }
        }
    }
    xhr.onerror = function(e) {
        console.log(e);
    }
    
    xhr.open( "GET", stl, true );
    //xhr.responseType = "arraybuffer";
    //xhr.setRequestHeader("Accept","text/plain");
    //xhr.setRequestHeader("Content-Type","text/plain");
    //xhr.setRequestHeader('charset', 'x-user-defined');
    xhr.send( null );
    
    renderer = new THREE.WebGLRenderer({ antialias: true }); //new THREE.CanvasRenderer();
    renderer.setSize( $(el).width(), $(el).height() );
    $(el).html(renderer.domElement);
}

function animate() {
    // note: three.js includes requestAnimationFrame shim
    requestAnimationFrame( animate );
    if(controls != undefined){
        controls.update();
    }
}

function render() {
    if(renderer != undefined){
        renderer.render( scene, camera );
    }
}
animate();
