from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Literal, Any, Optional, Union
import re
import numpy as np

# Import NetKet components
import netket.graph as nkgraph
import netket.hilbert as nkh
import netket.experimental as nkx
from netket.experimental.operator.fermion import destroy as c
from netket.experimental.operator.fermion import create as cdag

class LatticeSchema(BaseModel):
    """
    Represents a quantum lattice with text-based specification.
    
    Converts text descriptions like "4x4 square lattice" to NetKet graph objects.
    Supports various lattice types: chain, square, triangular, kagome, honeycomb, etc.
    """
    
    lattice_type: str = Field(
        description="Lattice type: 'chain', 'square', 'triangular', 'kagome', 'honeycomb', 'fcc', 'bcc', 'pyrochlore', 'cube', 'hypercube'"
    )
    
    extent: list[int] = Field(
        description="Lattice dimensions, e.g., [4] for 1D chain, [4,4] for 2D square, [2,2,2] for 3D cube"
    )
    
    text: str | None = Field(
        default=None,
        description="Text description like '4x4 square lattice' or 'chain of 8 sites'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate lattice_type and extent."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            
            # Parse various lattice descriptions
            parsed = cls._parse_lattice_text(text)
            data['lattice_type'] = parsed['lattice_type']
            data['extent'] = parsed['extent']
            
        return data
    
    @classmethod
    def _parse_lattice_text(cls, text: str) -> dict:
        """Parse lattice text descriptions."""
        text_lower = text.lower()
        
        # 1D patterns
        if "chain" in text_lower:
            # "chain of 8 sites", "8-site chain", "chain 8", "1D chain with 2 sites"
            match = re.search(r'(?:(\d+)(?:\s*sites?)?\s*chain)|(?:chain\s*(?:of|with)?\s*(\d+)(?:\s*sites?)?)', text_lower)
            if match:
                size = int(match.group(1) or match.group(2))
                return {"lattice_type": "chain", "extent": [size]}
        
        # 2D patterns
        elif "square" in text_lower:
            # "4x4 square lattice", "square lattice 4x4", "4x4 square"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*square|square\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "square", "extent": dims}
        
        elif "triangular" in text_lower:
            # "3x3 triangular lattice", "triangular lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*triangular|triangular\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "triangular", "extent": dims}
        
        elif "kagome" in text_lower:
            # "3x3 kagome lattice", "kagome lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*kagome|kagome\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "kagome", "extent": dims}
        
        elif "honeycomb" in text_lower:
            # "3x3 honeycomb lattice", "honeycomb lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*honeycomb|honeycomb\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "honeycomb", "extent": dims}
        
        # 3D patterns
        elif "cube" in text_lower or "cubic" in text_lower:
            # "2x2x2 cubic lattice", "cube 2x2x2", "2x2x2 cube"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*(?:cubic?|cube)|(?:cubic?|cube)\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "cube", "extent": dims}
        
        elif "fcc" in text_lower:
            # "2x2x2 fcc lattice", "fcc 2x2x2"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*fcc|fcc\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "fcc", "extent": dims}
        
        elif "bcc" in text_lower:
            # "2x2x2 bcc lattice", "bcc 2x2x2"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*bcc|bcc\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "bcc", "extent": dims}
        
        # Higher dimensional
        elif "hypercube" in text_lower:
            # "hypercube 4", "4D hypercube"
            match = re.search(r'hypercube\s*(\d+)|(\d+)d?\s*hypercube', text_lower)
            if match:
                dim = int(match.group(1) or match.group(2))
                return {"lattice_type": "hypercube", "extent": [dim]}
        
        # Fallback: try to extract dimensions
        match = re.search(r'(\d+)(?:\s*x\s*(\d+))?(?:\s*x\s*(\d+))?', text)
        if match:
            dims = [int(x) for x in match.groups() if x is not None]
            if len(dims) == 1:
                return {"lattice_type": "chain", "extent": dims}
            elif len(dims) == 2:
                return {"lattice_type": "square", "extent": dims}
            elif len(dims) == 3:
                return {"lattice_type": "cube", "extent": dims}
        
        raise ValueError(f"Could not parse lattice description: '{text}'. Supported formats: '4x4 square lattice', 'chain of 8 sites', '2x2x2 cubic lattice', etc.")
    
    @field_validator('lattice_type')
    @classmethod
    def validate_lattice_type(cls, v: str) -> str:
        """Validate lattice type."""
        valid_types = ['chain', 'square', 'triangular', 'kagome', 'honeycomb', 
                      'fcc', 'bcc', 'pyrochlore', 'cube', 'hypercube']
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid lattice type: {v}. Valid types: {valid_types}")
        return v.lower()
    
    @field_validator('extent')
    @classmethod
    def validate_extent(cls, v: list[int]) -> list[int]:
        """Validate extent dimensions."""
        if not v or len(v) == 0:
            raise ValueError("Extent must be a non-empty list of positive integers")
        if not all(isinstance(x, int) and x > 0 for x in v):
            raise ValueError("All extent values must be positive integers")
        return v
    
    def to_netket_graph(self) -> Any:
        """Convert to NetKet graph object."""
        lattice_map = {
            'chain': ('length', nkgraph.Chain),
            'square': ('length', nkgraph.Square),
            'cube': ('length', nkgraph.Cube),
            'hypercube': ('length', nkgraph.Hypercube),
            'triangular': ('extent', nkgraph.Triangular),
            'kagome': ('extent', nkgraph.Kagome),
            'honeycomb': ('extent', nkgraph.Honeycomb),
            'fcc': ('extent', nkgraph.FCC),
            'bcc': ('extent', nkgraph.BCC),
            'pyrochlore': ('extent', nkgraph.Pyrochlore),
        }
        arg_name, graph_class = lattice_map.get(self.lattice_type, (None, None))
        if not graph_class:
            raise ValueError(f"Unsupported lattice type: {self.lattice_type}")

        # Chain: length=int
        if self.lattice_type == "chain":
            return graph_class(length=self.extent[0])
        # Square: length=int (only n x n)
        elif self.lattice_type == "square":
            if len(self.extent) == 2 and self.extent[0] == self.extent[1]:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Square only supports n x n lattices. Use e.g. [4, 4].")
        # Cube: length=int (only n x n x n)
        elif self.lattice_type == "cube":
            if len(self.extent) == 3 and self.extent[0] == self.extent[1] == self.extent[2]:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Cube only supports n x n x n lattices. Use e.g. [2, 2, 2].")
        # Hypercube: length=int (only n)
        elif self.lattice_type == "hypercube":
            if len(self.extent) == 1:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Hypercube only supports a single dimension. Use e.g. [4].")
        # All others: extent=[...]
        else:
            return graph_class(extent=self.extent)
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        if self.lattice_type == 'chain':
            self.text = f"chain of {self.extent[0]} sites"
        elif len(self.extent) == 2:
            self.text = f"{self.extent[0]}x{self.extent[1]} {self.lattice_type} lattice"
        elif len(self.extent) == 3:
            self.text = f"{self.extent[0]}x{self.extent[1]}x{self.extent[2]} {self.lattice_type} lattice"
        else:
            self.text = f"{self.lattice_type} lattice with extent {self.extent}"
        return self

class HilbertSpaceSchema(BaseModel):
    """
    Represents the Hilbert space of a quantum system with text-based specification.
    
    Converts text descriptions like:
    - "spin-1/2 on each site"
    - "fermions at half filling"
    - "8 fermions with spin-1/2"
    - "2 bosons in 3 modes"
    to NetKet Hilbert space specifications.
    """
    
    space_type: Literal["spin", "fermion", "boson"] = Field(
        description="Type of Hilbert space"
    )
    
    spin: float = Field(
        default=0.5, 
        description="Spin value (for spin/fermion spaces)"
    )
    
    n_particles: Optional[int] = Field(
        default=None, 
        description="Fixed particle number (for fermion/boson spaces)"
    )
    
    n_modes: int = Field(
        default=1, 
        description="Number of modes (for bosons)"
    )
    
    text: str | None = Field(
        default=None,
        description="Text description like 'spin-1/2 on each site' or '8 fermions with spin-1/2'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate Hilbert space properties."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            parsed = cls._parse_hilbert_text(text)
            data.update(parsed)
        return data
    
    @classmethod
    def _parse_hilbert_text(cls, text: str) -> dict:
        """Parse Hilbert space text descriptions."""
        text_lower = text.lower()
        
        # Get particle number if specified
        number_match = re.search(r'(\d+)\s*(?:particles?|fermions?|bosons?)', text_lower)
        n_particles = int(number_match.group(1)) if number_match else None
        
        # Get spin if specified
        spin_match = re.search(r'spin[-\s]?(\d+(?:/\d+)?)', text_lower)
        if spin_match:
            spin_str = spin_match.group(1)
            if '/' in spin_str:
                num, denom = spin_str.split('/')
                spin = float(int(num)) / float(int(denom))
            else:
                spin = float(int(spin_str))
        else:
            spin = 0.5  # Default spin-1/2
        
        # Fermionic space
        if "fermion" in text_lower:
            return {
                "space_type": "fermion",
                "spin": spin,
                "n_particles": n_particles
            }
        
        # Bosonic space
        elif "boson" in text_lower:
            modes_match = re.search(r'(\d+)\s*modes?', text_lower)
            n_modes = int(modes_match.group(1)) if modes_match else 1
            
            return {
                "space_type": "boson",
                "n_particles": n_particles,
                "n_modes": n_modes
            }
            
        # Spin space (default)
        else:
            return {
                "space_type": "spin",
                "spin": spin
            }
    
    @field_validator('n_particles')
    @classmethod
    def validate_n_particles(cls, v: Optional[int], info) -> Optional[int]:
        """Validate particle number."""
        if info.data.get('space_type') in ['fermion', 'boson'] and v is None:
            raise ValueError("Number of particles must be specified for fermion/boson spaces")
        if v is not None and v <= 0:
            raise ValueError("Number of particles must be positive")
        return v
    
    def to_netket_hilbert(self, graph: Any) -> Any:
        """Convert to NetKet Hilbert space."""
        if self.space_type == "spin":
            return nkh.Spin(s=self.spin, N=graph.n_nodes)
        
        elif self.space_type == "fermion":
            if self.n_particles is None:
                raise ValueError("Number of particles must be specified for fermion space")
            return nkx.hilbert.SpinOrbitalFermions(
                graph.n_nodes, 
                s=self.spin, 
                n_fermions=self.n_particles
            )
        
        elif self.space_type == "boson":
            if self.n_particles is None:
                raise ValueError("Number of particles must be specified for boson space")
            return nkh.Fock(
                n_particles=self.n_particles, 
                N=self.n_modes, 
                n_max=None
            )
        
        else:
            raise ValueError(f"Unsupported Hilbert space type: {self.space_type}")
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        if self.space_type == "spin":
            if self.spin == 0.5:
                self.text = "spin-1/2 on each site"
            else:
                self.text = f"spin-{self.spin} on each site"
        
        elif self.space_type == "fermion":
            if self.n_particles:
                if self.spin == 0.5:
                    self.text = f"{self.n_particles} fermions with spin-1/2"
                else:
                    self.text = f"{self.n_particles} fermions with spin-{self.spin}"
            else:
                self.text = "fermions"
        
        elif self.space_type == "boson":
            if self.n_particles:
                if self.n_modes == 1:
                    self.text = f"{self.n_particles} bosons"
                else:
                    self.text = f"{self.n_particles} bosons in {self.n_modes} modes"
            else:
                self.text = "bosons"
        
        return self

class HamiltonianSchema(BaseModel):
    """
    Represents quantum Hamiltonians with text-based specification.
    
    Converts text descriptions like "Hubbard model with t=1, U=4" to NetKet Hamiltonian parameters.
    """
    
    # Fermion parameters
    hopping: float = Field(default=0.0, description="Hopping strength t")
    hubbard_u: float = Field(default=0.0, description="Hubbard interaction U")
    coulomb_v: float = Field(default=0.0, description="Nearest-neighbor Coulomb V")
    zeeman_b: float = Field(default=0.0, description="Zeeman field B")
    
    # Spin parameters
    heisenberg_j: float = Field(default=0.0, description="Heisenberg exchange J")
    ising_jz: float = Field(default=0.0, description="Ising coupling Jz")
    transverse_hx: float = Field(default=0.0, description="Transverse field hx")
    longitudinal_hz: float = Field(default=0.0, description="Longitudinal field hz")
    
    # Boson parameters
    chemical_potential: float = Field(default=0.0, description="Chemical potential μ")
    
    # Model type inference
    model_type: Optional[str] = Field(default=None, description="Inferred model type")
    
    text: str | None = Field(
        default=None,
        description="Text description like 'Hubbard model with t=1, U=4' or 'Heisenberg model with J=1, hx=0.5'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate Hamiltonian parameters."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            parsed = cls._parse_hamiltonian_text(text)
            data.update(parsed)
        return data
    
    @classmethod
    def _parse_hamiltonian_text(cls, text: str) -> dict:
        """Parse Hamiltonian text descriptions."""
        text_lower = text.lower()
        params = {}
        
        # Model type detection
        if "hubbard" in text_lower:
            params["model_type"] = "hubbard"
        elif "heisenberg" in text_lower:
            params["model_type"] = "heisenberg"
        elif "ising" in text_lower:
            params["model_type"] = "ising"
        elif "kitaev" in text_lower:
            params["model_type"] = "kitaev"
        
        # Parameter extraction patterns
        param_patterns = [
            (r't\s*=\s*([+-]?\d*\.?\d+)', 'hopping'),
            (r'u\s*=\s*([+-]?\d*\.?\d+)', 'hubbard_u'),
            (r'v\s*=\s*([+-]?\d*\.?\d+)', 'coulomb_v'),
            (r'b\s*=\s*([+-]?\d*\.?\d+)', 'zeeman_b'),
            (r'j\s*=\s*([+-]?\d*\.?\d+)', 'heisenberg_j'),
            (r'jz\s*=\s*([+-]?\d*\.?\d+)', 'ising_jz'),
            (r'hx\s*=\s*([+-]?\d*\.?\d+)', 'transverse_hx'),
            (r'hz\s*=\s*([+-]?\d*\.?\d+)', 'longitudinal_hz'),
            (r'μ\s*=\s*([+-]?\d*\.?\d+)|mu\s*=\s*([+-]?\d*\.?\d+)', 'chemical_potential'),
        ]
        
        for pattern, param_name in param_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1) or match.group(2))
                params[param_name] = value
        
        # Special cases for common model names
        if "hubbard model" in text_lower and not any(k in params for k in ['hopping', 'hubbard_u']):
            # Default Hubbard parameters if not specified
            params.setdefault("hopping", 1.0)
            params.setdefault("hubbard_u", 4.0)
        
        elif "heisenberg model" in text_lower and not any(k in params for k in ['heisenberg_j', 'transverse_hx']):
            # Default Heisenberg parameters if not specified
            params.setdefault("heisenberg_j", 1.0)
        
        if not params.get("model_type") and all(params.get(k, 0.0) == 0.0 for k in [
            "hopping", "hubbard_u", "coulomb_v", "zeeman_b",
            "heisenberg_j", "ising_jz", "transverse_hx", "longitudinal_hz", "chemical_potential"
        ]):
            raise ValueError(f"Could not parse Hamiltonian description: '{text}'. "
                             "Supported formats: 'Hubbard model with t=1, U=4', 'Heisenberg model with J=1, hx=0.5', etc.")
        
        return params
    
    def to_netket_hamiltonian(self, hilbert: Any, graph: Any) -> Any:
        """Convert to NetKet Hamiltonian operator."""
        from fermion_builder import Hop, Hubbard, Coulomb, Zeeman
        
        hamiltonian = 0.0
        
        # Fermion terms
        if self.hopping != 0.0:
            hamiltonian += Hop(hilbert, graph, self.hopping)
        
        if self.hubbard_u != 0.0:
            hamiltonian += Hubbard(hilbert, graph, self.hubbard_u)
        
        if self.coulomb_v != 0.0:
            hamiltonian += Coulomb(hilbert, graph, self.coulomb_v)
        
        if self.zeeman_b != 0.0:
            hamiltonian += Zeeman(hilbert, graph, self.zeeman_b)
        
        # Spin terms (would need to implement spin operators)
        # For now, return fermion Hamiltonian
        # TODO: Add spin Hamiltonian construction
        
        return hamiltonian
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        terms = []
        
        # Determine model type if not set
        if not self.model_type:
            if self.hubbard_u != 0.0 or self.hopping != 0.0:
                self.model_type = "hubbard"
            elif self.heisenberg_j != 0.0:
                self.model_type = "heisenberg"
            elif self.ising_jz != 0.0:
                self.model_type = "ising"
        
        # Build description
        if self.model_type:
            terms.append(f"{self.model_type.title()} model")
        
        # Add parameters
        param_descriptions = []
        if self.hopping != 0.0:
            param_descriptions.append(f"t={self.hopping}")
        if self.hubbard_u != 0.0:
            param_descriptions.append(f"U={self.hubbard_u}")
        if self.coulomb_v != 0.0:
            param_descriptions.append(f"V={self.coulomb_v}")
        if self.zeeman_b != 0.0:
            param_descriptions.append(f"B={self.zeeman_b}")
        if self.heisenberg_j != 0.0:
            param_descriptions.append(f"J={self.heisenberg_j}")
        if self.ising_jz != 0.0:
            param_descriptions.append(f"Jz={self.ising_jz}")
        if self.transverse_hx != 0.0:
            param_descriptions.append(f"hx={self.transverse_hx}")
        if self.longitudinal_hz != 0.0:
            param_descriptions.append(f"hz={self.longitudinal_hz}")
        
        if param_descriptions:
            terms.append("with " + ", ".join(param_descriptions))
        
        self.text = " ".join(terms) if terms else "empty Hamiltonian"
        return self


# Utility function for creating schemas from text
def create_lattice_from_text(text: str) -> LatticeSchema:
    """Create LatticeSchema from text description."""
    return LatticeSchema(text=text)

def create_particles_from_text(text: str) -> HilbertSpaceSchema:
    """Create HilbertSpaceSchema from text description."""
    return HilbertSpaceSchema(text=text)

def create_hamiltonian_from_text(text: str) -> HamiltonianSchema:
    """Create HamiltonianSchema from text description."""
    return HamiltonianSchema(text=text) 