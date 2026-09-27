// three.js と使用するアドオンを1ファイルにまとめる（file:// で開けるように IIFE 化）
// ビルド: npx esbuild vendor/entry.js --bundle --format=iife --minify --outfile=vendor/three-bundle.js
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
window.THREE = THREE;
window.THREEX = { EffectComposer, RenderPass, UnrealBloomPass, OutputPass, mergeGeometries };
