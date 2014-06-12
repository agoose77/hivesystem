import spyder
spyder.delete_wisdom()
spyder.loader.recompile = None
import spyder.modules.core
import spyder.modules.builtin
import spyder.modules.basic
import spyder.modules.tarantula
import spyder.modules.models3d
import spyder.modules.canvas
import spyder.modules.hivemap
import spyder.modules.http
import spyder.modules.atom
spyder.write_wisdom()
